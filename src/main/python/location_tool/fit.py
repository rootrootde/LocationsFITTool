from datetime import datetime, timezone
from typing import Callable, List, Optional, Tuple

from fit_tool.data_message import DataMessage
from fit_tool.fit_file import FitFile
from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.course_message import CourseMessage
from fit_tool.profile.messages.course_point_message import CoursePointMessage
from fit_tool.profile.messages.file_creator_message import FileCreatorMessage
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.lap_message import LapMessage
from fit_tool.profile.messages.location_message import LocationMessage
from fit_tool.profile.messages.location_settings_message import LocationSettingsMessage
from fit_tool.profile.messages.record_message import RecordMessage
from fit_tool.profile.messages.session_message import SessionMessage
from fit_tool.profile.profile_type import (
    CoursePoint,
    Event,
    EventType,
    FileType,
    GarminProduct,
    LocationSettings,
    Manufacturer,
    MapSymbol,
    Sport,
    SubSport,
)

from . import logger
from .fit_data import (
    ActivityFitFileData,
    CourseMessageData,
    CoursePointMessageData,
    CoursesFitFileData,
    FileCreatorMessageData,
    FileIdMessageData,
    LapMessageData,
    LocationMessageData,
    LocationSettingsMessageData,
    LocationsFitFileData,
    RecordMessageData,
    SessionMessageData,
)
from .tracks import RouteData, TrackData
from .waypoints import WaypointData

# Define conservative maximum character lengths for truncation
MAX_NAME_CHARS = 50
MAX_DESC_CHARS = 50


class FitFileHandler:
    def __init__(self, appctxt):
        """Initialize the FIT file handler."""
        self.appctxt = appctxt
        self.logger = logger.Logger.get_logger()

    def parse_fit_file(
        self, file_path: str, logger: Optional[Callable[[str], None]] = None
    ) -> LocationsFitFileData | CoursesFitFileData | ActivityFitFileData | None:
        """Parse a FIT file and return appropriate FitFileData (Locations, Courses, or Activity)."""
        locations_data = LocationsFitFileData()
        courses_data = CoursesFitFileData()
        activity_data = ActivityFitFileData()

        parsed_waypoints = []
        parsed_records = []
        parsed_laps = []
        parsed_sessions = []

        is_locations_file = False
        is_courses_file = False
        is_activity_file = False

        try:
            fit_file = FitFile.from_file(file_path)
        except Exception as e:
            self.logger.error(f"Error opening or parsing FIT file: {e}")
            return None

        file_id_message_data = None
        file_creator_message_data = None

        for record_wrapper in fit_file.records:
            actual_message = record_wrapper.message
            if not isinstance(actual_message, DataMessage):
                continue
            global_id = actual_message.definition_message.global_id

            if global_id == FileIdMessage.ID:
                msg = actual_message
                file_type_val = getattr(msg, "type", None)
                file_type_enum = None
                if file_type_val is not None:
                    try:
                        file_type_enum = FileType(file_type_val)
                    except ValueError:
                        self.logger.error(f"Invalid FileType value: {file_type_val}")

                manufacturer_val = getattr(msg, "manufacturer", None)
                manufacturer_enum = None
                if manufacturer_val is not None:
                    try:
                        manufacturer_enum = Manufacturer(manufacturer_val)
                    except ValueError:
                        self.logger.error(f"Invalid Manufacturer value: {manufacturer_val}")

                product_id_val = getattr(msg, "product", None)
                garmin_product_enum = None
                if manufacturer_enum == Manufacturer.GARMIN and product_id_val is not None:
                    try:
                        garmin_product_enum = GarminProduct(product_id_val)
                    except ValueError:
                        self.logger.error(f"Invalid GarminProduct: {product_id_val}")

                file_id_message_data = FileIdMessageData(
                    file_type=file_type_enum,
                    manufacturer=manufacturer_enum,
                    product=garmin_product_enum if garmin_product_enum else product_id_val,
                    serial_number=getattr(msg, "serial_number", None),
                    time_created=getattr(msg, "time_created", None),
                    product_name=getattr(msg, "product_name", None),
                )
                if file_type_enum == FileType.LOCATIONS:
                    is_locations_file = True
                elif file_type_enum == FileType.COURSES:
                    is_courses_file = True
                elif file_type_enum == FileType.ACTIVITY:
                    is_activity_file = True
                break

        if not file_id_message_data:
            file_id_message_data = FileIdMessageData(file_type=FileType.DEVICE)

        locations_data.file_id = file_id_message_data
        courses_data.file_id = file_id_message_data
        activity_data.file_id = file_id_message_data

        for record_wrapper in fit_file.records:
            actual_message = record_wrapper.message
            if not isinstance(actual_message, DataMessage):
                continue
            global_id = actual_message.definition_message.global_id

            try:
                if global_id == FileIdMessage.ID:
                    pass

                elif global_id == FileCreatorMessage.ID:
                    msg = actual_message
                    file_creator_message_data = FileCreatorMessageData(
                        software_version=getattr(msg, "software_version", None),
                        hardware_version=getattr(msg, "hardware_version", None),
                    )
                    locations_data.creator = file_creator_message_data
                    courses_data.creator = file_creator_message_data
                    activity_data.creator = file_creator_message_data

                elif global_id == LocationSettingsMessage.ID and (
                    is_locations_file or not (is_courses_file or is_activity_file)
                ):
                    msg = actual_message
                    location_settings_raw = getattr(msg, "location_settings", None)
                    location_settings_enum = None
                    if location_settings_raw is not None:
                        try:
                            location_settings_enum = LocationSettings(location_settings_raw)
                        except ValueError:
                            self.logger.error(f"Invalid LocationSettings: {location_settings_raw}")
                    locations_data.location_settings = LocationSettingsMessageData(
                        location_settings_enum=location_settings_enum
                    )
                    if not is_locations_file and not is_courses_file and not is_activity_file:
                        is_locations_file = True

                elif global_id == LocationMessage.ID and (
                    is_locations_file or not (is_courses_file or is_activity_file)
                ):
                    msg = actual_message
                    lat_degrees = getattr(msg, "position_lat", None)
                    lon_degrees = getattr(msg, "position_long", None)
                    location_datetime_object = getattr(msg, "timestamp", None)

                    symbol_val = getattr(msg, "symbol", None)
                    symbol_enum = MapSymbol.AIRPORT
                    if symbol_val is not None:
                        try:
                            symbol_enum = MapSymbol(symbol_val)
                        except ValueError:
                            self.logger.error(f"Invalid MapSymbol: {symbol_val}")

                    waypoint = WaypointData(
                        name=getattr(msg, "location_name", None),
                        description=getattr(msg, "description", None),
                        latitude=lat_degrees if lat_degrees is not None else 0.0,
                        longitude=lon_degrees if lon_degrees is not None else 0.0,
                        elevation=getattr(msg, "altitude", None),
                        timestamp=location_datetime_object
                        if location_datetime_object
                        else datetime.now(timezone.utc),
                        symbol=symbol_enum,
                        message_index=getattr(msg, "message_index", None),
                    )
                    parsed_waypoints.append(waypoint)
                    if not is_locations_file and not is_courses_file and not is_activity_file:
                        is_locations_file = True

                elif global_id == CourseMessage.ID and is_courses_file:
                    msg = actual_message
                    sport_val = getattr(msg, "sport", None)
                    sport_enum = None
                    if sport_val is not None:
                        try:
                            sport_enum = Sport(sport_val)
                        except ValueError:
                            self.logger.warning(
                                f"Invalid Sport value in CourseMessage: {sport_val}"
                            )

                    sub_sport_val = getattr(msg, "sub_sport", None)
                    sub_sport_enum = None
                    if sub_sport_val is not None:
                        try:
                            sub_sport_enum = SubSport(sub_sport_val)
                        except ValueError:
                            self.logger.warning(
                                f"Invalid SubSport value in CourseMessage: {sub_sport_val}"
                            )

                    course_name = getattr(msg, "name", f"Course {len(courses_data.courses) + 1}")

                    # Ensure course_name is not None and truncate if necessary
                    if course_name is None:
                        course_name = f"Unnamed Course {len(courses_data.courses) + 1}"
                    elif len(course_name) > MAX_NAME_CHARS:
                        course_name = course_name[:MAX_NAME_CHARS]

                    course_data = CourseMessageData(
                        name=course_name,
                        sport=sport_enum,
                        sub_sport=sub_sport_enum,
                        capabilities=getattr(msg, "capabilities", None),
                        message_index=getattr(msg, "message_index", None),
                    )
                    courses_data.courses.append(course_data)

                elif global_id == CoursePointMessage.ID and is_courses_file:
                    msg = actual_message
                    lat_degrees = getattr(msg, "position_lat", None)
                    lon_degrees = getattr(msg, "position_long", None)
                    timestamp = getattr(msg, "timestamp", None)  # Can be None for course points

                    point_type_val = getattr(msg, "type", None)
                    point_type_enum = None
                    if point_type_val is not None:
                        try:
                            point_type_enum = CoursePoint(point_type_val)
                        except ValueError:
                            self.logger.warning(f"Invalid CoursePoint type value: {point_type_val}")

                    point_name = getattr(msg, "name", None)
                    # Truncate point_name if necessary
                    if point_name and len(point_name) > MAX_NAME_CHARS:
                        point_name = point_name[:MAX_NAME_CHARS]

                    course_point_data = CoursePointMessageData(
                        timestamp=timestamp,
                        position_lat=lat_degrees,
                        position_long=lon_degrees,
                        distance=getattr(msg, "distance", None),
                        type=point_type_enum,
                        name=point_name,
                        favorite=getattr(msg, "favorite", None),
                        message_index=getattr(msg, "message_index", None),
                    )

                    # Find the parent course for this course point
                    # Course points should ideally follow their course message or be associated by message_index
                    # For simplicity, we'll add to the last parsed course if available.
                    # A more robust solution might involve matching course_message_index if available.
                    if courses_data.courses:
                        courses_data.courses[-1].points.append(course_point_data)
                    else:
                        self.logger.warning(
                            "CoursePointMessage found without a preceding CourseMessage. Skipping."
                        )

                elif global_id == RecordMessage.ID and (
                    is_activity_file
                    or not (
                        is_locations_file or is_courses_file
                    )  # If type unknown, assume activity
                ):
                    msg = actual_message
                    # Ensure timestamp is not None, provide a default if it is
                    timestamp = getattr(msg, "timestamp", None)
                    if timestamp is None:
                        timestamp = datetime.now(timezone.utc)
                        self.logger.warning(
                            "RecordMessage found with no timestamp. Using current time."
                        )

                    record = RecordMessageData(
                        timestamp=timestamp,
                        position_lat=getattr(msg, "position_lat", None),
                        position_long=getattr(msg, "position_long", None),
                        altitude=getattr(msg, "altitude", None),
                        heart_rate=getattr(msg, "heart_rate", None),
                        cadence=getattr(msg, "cadence", None),
                        distance=getattr(msg, "distance", None),
                        speed=getattr(msg, "speed", None),
                        power=getattr(msg, "power", None),
                        grade=getattr(msg, "grade", None),
                    )
                    parsed_records.append(record)
                    if not is_activity_file and not is_locations_file and not is_courses_file:
                        is_activity_file = True
                        activity_data.file_id.file_type = (
                            FileType.ACTIVITY
                        )  # Update file type if it was generic

                elif global_id == LapMessage.ID and (
                    is_activity_file
                    or not (
                        is_locations_file or is_courses_file
                    )  # If type unknown, assume activity
                ):
                    msg = actual_message
                    # Ensure start_time and timestamp are not None
                    start_time = getattr(msg, "start_time", None)
                    if start_time is None:
                        start_time = datetime.now(timezone.utc)
                        self.logger.warning(
                            "LapMessage found with no start_time. Using current time."
                        )

                    timestamp = getattr(msg, "timestamp", None)  # This is lap end time
                    if timestamp is None:
                        timestamp = start_time  # Or handle as an error / use last record time
                        self.logger.warning(
                            "LapMessage found with no end timestamp. Using start_time."
                        )

                    lap = LapMessageData(
                        timestamp=timestamp,
                        start_time=start_time,
                        total_elapsed_time=getattr(msg, "total_elapsed_time", 0.0),
                        total_timer_time=getattr(msg, "total_timer_time", 0.0),
                        start_position_lat=getattr(msg, "start_position_lat", None),
                        start_position_long=getattr(msg, "start_position_long", None),
                        end_position_lat=getattr(msg, "end_position_lat", None),
                        end_position_long=getattr(msg, "end_position_long", None),
                        total_distance=getattr(msg, "total_distance", None),
                        avg_speed=getattr(msg, "avg_speed", None),
                        max_speed=getattr(msg, "max_speed", None),
                        avg_heart_rate=getattr(msg, "avg_heart_rate", None),
                        max_heart_rate=getattr(msg, "max_heart_rate", None),
                        avg_cadence=getattr(msg, "avg_cadence", None),
                        max_cadence=getattr(msg, "max_cadence", None),
                        sport=Sport(getattr(msg, "sport", Sport.GENERIC.value)),  # Provide default
                        message_index=getattr(msg, "message_index", None),
                    )
                    parsed_laps.append(lap)
                    if not is_activity_file and not is_locations_file and not is_courses_file:
                        is_activity_file = True
                        activity_data.file_id.file_type = FileType.ACTIVITY

                elif global_id == SessionMessage.ID and (
                    is_activity_file
                    or not (
                        is_locations_file or is_courses_file
                    )  # If type unknown, assume activity
                ):
                    msg = actual_message
                    # Ensure start_time and timestamp are not None
                    start_time = getattr(msg, "start_time", None)
                    if start_time is None:
                        start_time = datetime.now(timezone.utc)
                        self.logger.warning(
                            "SessionMessage found with no start_time. Using current time."
                        )

                    timestamp = getattr(msg, "timestamp", None)  # This is session end time
                    if timestamp is None:
                        timestamp = start_time  # Or handle as an error / use last record time
                        self.logger.warning(
                            "SessionMessage found with no end timestamp. Using start_time."
                        )

                    sport_val = getattr(msg, "sport", Sport.GENERIC.value)
                    sport_enum = Sport.GENERIC
                    try:
                        sport_enum = Sport(sport_val)
                    except ValueError:
                        self.logger.warning(f"Invalid Sport value in SessionMessage: {sport_val}")

                    sub_sport_val = getattr(msg, "sub_sport", SubSport.GENERIC.value)
                    sub_sport_enum = SubSport.GENERIC
                    try:
                        sub_sport_enum = SubSport(sub_sport_val)
                    except ValueError:
                        self.logger.warning(
                            f"Invalid SubSport value in SessionMessage: {sub_sport_val}"
                        )

                    session = SessionMessageData(
                        timestamp=timestamp,  # Session end time
                        start_time=start_time,
                        total_elapsed_time=getattr(msg, "total_elapsed_time", 0.0),
                        total_timer_time=getattr(msg, "total_timer_time", 0.0),
                        total_distance=getattr(msg, "total_distance", None),
                        sport=sport_enum,
                        sub_sport=sub_sport_enum,
                        first_lap_index=getattr(msg, "first_lap_index", 0),
                        num_laps=getattr(msg, "num_laps", 0),
                        message_index=getattr(msg, "message_index", None),
                    )
                    parsed_sessions.append(session)
                    if not is_activity_file and not is_locations_file and not is_courses_file:
                        is_activity_file = True
                        activity_data.file_id.file_type = FileType.ACTIVITY

            except AttributeError as e:
                self.logger.error(
                    f"Attr err processing {type(actual_message).__name__} (Global ID: {global_id}): {e}"
                )
            except ValueError as e:
                self.logger.error(
                    f"Value err processing {type(actual_message).__name__} (Global ID: {global_id}): {e}"
                )
            except Exception as e:
                self.logger.error(
                    f"Unexpected err processing {type(actual_message).__name__} (Global ID: {global_id}): {e}"
                )

        if is_locations_file:
            locations_data.locations = parsed_waypoints
            if (
                not locations_data.locations
                and not file_id_message_data.file_type == FileType.LOCATIONS
            ):
                # If no locations found and file type wasn't explicitly locations, this isn't a locations file.
                pass  # Let it fall through to check other types or return None
            else:
                return locations_data

        if is_courses_file:
            # Associate course points with courses if not already done (e.g. if they are not ordered)
            # This is a simplified association, assuming course points belong to the course with the same message_index
            # or the chronologically last course if message_index is not reliable.
            # For now, the current implementation adds points to the last parsed course, which is a common case.
            if not courses_data.courses and not file_id_message_data.file_type == FileType.COURSES:
                pass
            else:
                return courses_data

        if is_activity_file:
            # Basic assembly: group records by lap/session if possible, or as a single track.
            # For now, we'll treat all records as part of one continuous track if no laps/sessions,
            # or associate them based on lap/session data if present.

            if not parsed_records and not file_id_message_data.file_type == FileType.ACTIVITY:
                pass  # Not an activity file if no records and not explicitly activity type
            else:
                activity_data.records = parsed_records
                activity_data.laps = parsed_laps
                activity_data.sessions = parsed_sessions
                # If there are records but no sessions, create a default session
                if parsed_records and not parsed_sessions:
                    self.logger.info(
                        "No session messages found in activity, creating a default session."
                    )
                    default_session_start_time = (
                        parsed_records[0].timestamp
                        if parsed_records
                        else datetime.now(timezone.utc)
                    )
                    default_session_end_time = (
                        parsed_records[-1].timestamp
                        if parsed_records
                        else default_session_start_time
                    )
                    default_session = SessionMessageData(
                        timestamp=default_session_end_time,
                        start_time=default_session_start_time,
                        total_elapsed_time=(
                            default_session_end_time - default_session_start_time
                        ).total_seconds(),
                        total_timer_time=(
                            default_session_end_time - default_session_start_time
                        ).total_seconds(),
                        sport=Sport.GENERIC,  # Default sport
                        num_laps=len(parsed_laps) if parsed_laps else (1 if parsed_records else 0),
                    )
                    activity_data.sessions.append(default_session)

                # If there are records but no laps (and sessions might exist or be default)
                if parsed_records and not parsed_laps and activity_data.sessions:
                    self.logger.info(
                        "No lap messages found in activity, creating a default lap per session."
                    )
                    new_laps = []
                    for session_idx, session_msg in enumerate(activity_data.sessions):
                        # Try to find records within this session's timeframe
                        session_records = [
                            r
                            for r in parsed_records
                            if session_msg.start_time <= r.timestamp <= session_msg.timestamp
                        ]
                        if not session_records:  # If no records in session, use session times
                            session_records_start_time = session_msg.start_time
                            session_records_end_time = session_msg.timestamp
                        else:
                            session_records_start_time = session_records[0].timestamp
                            session_records_end_time = session_records[-1].timestamp

                        default_lap = LapMessageData(
                            timestamp=session_records_end_time,  # Lap end time
                            start_time=session_records_start_time,  # Lap start time
                            total_elapsed_time=(
                                session_records_end_time - session_records_start_time
                            ).total_seconds(),
                            total_timer_time=(
                                session_records_end_time - session_records_start_time
                            ).total_seconds(),
                            sport=session_msg.sport,  # Use sport from session
                            message_index=session_msg.message_index
                            if session_msg.message_index is not None
                            else session_idx,
                        )
                        new_laps.append(default_lap)
                        # Update session's lap count if it was 0
                        if session_msg.num_laps == 0 and new_laps:
                            session_msg.num_laps = 1  # Assuming one default lap per session created
                            if session_msg.first_lap_index == 0 and len(activity_data.laps) > 0:
                                # This logic might need refinement if laps are added out of order or already exist
                                pass

                    activity_data.laps.extend(new_laps)
                    # Ensure sessions correctly reference these new laps if they were created ad-hoc
                    # This might involve updating first_lap_index and num_laps in existing session objects
                    # if they were not accurately reflecting the data or if we are creating default laps.
                    # For simplicity, we assume new_laps are the only laps if parsed_laps was empty.
                    if not parsed_laps and new_laps:  # if original parsed_laps was empty
                        for idx, session_msg in enumerate(activity_data.sessions):
                            session_msg.first_lap_index = (
                                idx  # Simplistic: assumes one lap per session, sequentially indexed
                            )
                            session_msg.num_laps = 1

                return activity_data

        # If, after checking all message types, no specific type was determined or no relevant data found
        self.logger.info(
            f"File {file_path} did not clearly match Locations, Courses, or Activity FIT file structure, or contained no relevant data."
        )
        return None

    def _build_file_id_message(
        self, file_id_data: FileIdMessageData, file_type_override: Optional[FileType] = None
    ):
        """Build a FileIdMessage from data."""
        fid_msg = FileIdMessage()

        actual_file_type = file_type_override if file_type_override else file_id_data.file_type
        fid_msg.type = actual_file_type if actual_file_type is not None else FileType.DEVICE

        fid_msg.manufacturer = (
            file_id_data.manufacturer
            if file_id_data.manufacturer is not None
            else Manufacturer.DEVELOPMENT
        )
        if file_id_data.product is not None:
            if isinstance(file_id_data.product, GarminProduct):
                fid_msg.product = file_id_data.product.value
            else:
                fid_msg.product = file_id_data.product
        else:
            fid_msg.product = 0 if fid_msg.manufacturer == Manufacturer.DEVELOPMENT.value else 1

        fid_msg.serial_number = (
            file_id_data.serial_number if file_id_data.serial_number is not None else 0
        )
        fid_msg.time_created = (
            file_id_data.time_created
            if file_id_data.time_created is not None
            else datetime.now(timezone.utc)
        )
        if file_id_data.product_name is not None:
            fid_msg.product_name = file_id_data.product_name
        return fid_msg

    def _build_file_creator_message(self, creator):
        """Build a FileCreatorMessage from data."""
        creator_msg = FileCreatorMessage()
        creator_msg.software_version = (
            creator.software_version if creator.software_version is not None else 0
        )
        creator_msg.hardware_version = (
            creator.hardware_version if creator.hardware_version is not None else 0
        )
        return creator_msg

    def _build_location_settings_message(self, location_settings):
        """Build a LocationSettingsMessage from data."""
        ls_msg = LocationSettingsMessage()
        ls_msg.location_settings = location_settings.location_settings_enum.value
        return ls_msg

    def _build_location_message(self, index, loc_data: LocationMessageData):
        """Build a LocationMessage from LocationMessageData."""
        loc_msg = LocationMessage()

        # Name and Description truncation
        loc_name = loc_data.name or "Waypoint"
        if len(loc_name) > MAX_NAME_CHARS:
            self.logger.warning(f"Location name '{loc_name}' truncated to {MAX_NAME_CHARS} chars.")
            loc_name = loc_name[:MAX_NAME_CHARS]
        loc_msg.location_name = loc_name

        if loc_data.description:
            loc_desc = loc_data.description
            if len(loc_desc) > MAX_DESC_CHARS:
                self.logger.warning(
                    f"Location description for '{loc_name}' truncated to {MAX_DESC_CHARS} chars."
                )
                loc_desc = loc_desc[:MAX_DESC_CHARS]
            loc_msg.description = loc_desc
        else:
            loc_msg.description = None

        if loc_data.latitude is not None and loc_data.longitude is not None:
            loc_msg.position_lat = loc_data.latitude
            loc_msg.position_long = loc_data.longitude
        else:
            self.logger.error(f"Skipping location/waypoint due to missing lat/lon: {loc_name}")
            return None  # Cannot create a location message without coordinates

        if loc_data.altitude is not None:
            loc_msg.altitude = loc_data.altitude

        loc_msg.timestamp = loc_data.timestamp if loc_data.timestamp else datetime.now(timezone.utc)

        if isinstance(loc_data.symbol, MapSymbol):
            loc_msg.symbol = loc_data.symbol.value
        elif isinstance(loc_data.symbol, int):
            try:
                MapSymbol(loc_data.symbol)  # Validate int is a valid MapSymbol value
                loc_msg.symbol = loc_data.symbol
            except ValueError:
                self.logger.warning(
                    f"Invalid integer symbol value {loc_data.symbol} for {loc_name}. Using default."
                )
                loc_msg.symbol = MapSymbol.FLAG_BLUE.value  # Default symbol
        elif loc_data.symbol is None:  # Explicitly handle None if symbol is optional
            loc_msg.symbol = MapSymbol.FLAG_BLUE.value  # Default if None
        else:  # Catch-all for unexpected symbol types
            self.logger.warning(
                f"Unexpected symbol type {type(loc_data.symbol)} for {loc_name}. Using default."
            )
            loc_msg.symbol = MapSymbol.FLAG_BLUE.value

        loc_msg.message_index = (
            loc_data.message_index if loc_data.message_index is not None else index
        )
        return loc_msg

    def _build_course_message(self, course_data: CourseMessageData, index: int) -> CourseMessage:
        """Build a CourseMessage from CourseMessageData."""
        course_msg = CourseMessage()
        course_name = course_data.name or f"Course {index + 1}"
        if len(course_name) > MAX_NAME_CHARS:
            self.logger.warning(f"Course name '{course_name}' truncated.")
        course_msg.name = course_name[:MAX_NAME_CHARS]

        if course_data.sport:
            course_msg.sport = course_data.sport.value
        else:  # Default sport if not provided
            course_msg.sport = Sport.GENERIC.value

        if course_data.sub_sport:
            course_msg.sub_sport = course_data.sub_sport.value
        # Not setting sub_sport if None, as it's optional

        if course_data.capabilities is not None:
            course_msg.capabilities = course_data.capabilities

        # message_index for courses is usually for ordering or identification if multiple courses in a file
        course_msg.message_index = (
            course_data.message_index if course_data.message_index is not None else index
        )
        return course_msg

    def _build_course_point_message(
        self,
        cp_data: CoursePointMessageData,
        index: int,
        course_message_index: Optional[int] = None,
    ) -> CoursePointMessage:
        """Build a CoursePointMessage from CoursePointMessageData."""
        cp_msg = CoursePointMessage()
        cp_name = cp_data.name or f"Point {index + 1}"
        if len(cp_name) > MAX_NAME_CHARS:
            self.logger.warning(f"Course point name '{cp_name}' truncated.")
        cp_msg.name = cp_name[:MAX_NAME_CHARS]

        if cp_data.timestamp:
            cp_msg.timestamp = cp_data.timestamp

        # Position is mandatory for most course points that are geographical
        if cp_data.position_lat is not None and cp_data.position_long is not None:
            cp_msg.position_lat = cp_data.position_lat
            cp_msg.position_long = cp_data.position_long
        elif cp_data.type not in [
            CoursePoint.SEGMENT_START,
            CoursePoint.SEGMENT_END,
        ]:  # Some types might not need lat/lon
            self.logger.warning(
                f"Course point '{cp_name}' missing position. It might not be displayed on a map."
            )
            # Depending on strictness, could return None or allow it

        if cp_data.distance is not None:
            cp_msg.distance = cp_data.distance

        if cp_data.type:
            cp_msg.type = cp_data.type.value
        else:
            cp_msg.type = CoursePoint.GENERIC.value  # Default type

        if cp_data.favorite is not None:
            cp_msg.favorite = cp_data.favorite

        cp_msg.message_index = cp_data.message_index if cp_data.message_index is not None else index
        # Optional: Link to parent course message if FIT profile supports/requires it (e.g. course_message_index field)
        # For now, standard CoursePointMessage does not have a direct course_message_index field.
        # Association is by order or by higher-level file structure.
        return cp_msg

    def _build_record_message(self, record_data: RecordMessageData) -> Optional[RecordMessage]:
        """Build a RecordMessage from RecordMessageData."""
        # Basic validation: A record message must have a timestamp and usually position for GPS tracks.
        if not record_data.timestamp:
            self.logger.error("Skipping Record message due to missing timestamp.")
            return None
        if record_data.position_lat is None or record_data.position_long is None:
            # Allow records without lat/lon if other sensor data is present (e.g. indoor activity)
            # However, for a typical GPS track, this would be an issue.
            self.logger.warning("Record message at {record_data.timestamp} has no position data.")

        rec_msg = RecordMessage()
        rec_msg.timestamp = record_data.timestamp
        if record_data.position_lat is not None:
            rec_msg.position_lat = record_data.position_lat
        if record_data.position_long is not None:
            rec_msg.position_long = record_data.position_long
        if record_data.altitude is not None:
            rec_msg.altitude = record_data.altitude
        if record_data.heart_rate is not None:
            rec_msg.heart_rate = record_data.heart_rate
        if record_data.cadence is not None:
            rec_msg.cadence = record_data.cadence
        if record_data.distance is not None:
            rec_msg.distance = record_data.distance
        if record_data.speed is not None:
            rec_msg.speed = record_data.speed
        if record_data.power is not None:
            rec_msg.power = record_data.power
        if record_data.grade is not None:
            rec_msg.grade = record_data.grade
        return rec_msg

    def _build_lap_message(self, lap_data: LapMessageData, index: int) -> LapMessage:
        """Build a LapMessage from LapMessageData."""
        lap_msg = LapMessage()
        lap_msg.timestamp = lap_data.timestamp  # Lap end time
        lap_msg.message_index = (
            lap_data.message_index if lap_data.message_index is not None else index
        )

        if lap_data.start_time:
            lap_msg.start_time = lap_data.start_time
        else:
            self.logger.warning(
                f"Lap (idx {index}) missing start_time. Defaulting to lap end time. This may cause issues."
            )
            lap_msg.start_time = lap_data.timestamp

        lap_msg.event = Event.LAP
        lap_msg.event_type = EventType.STOP
        if hasattr(lap_data, "event") and lap_data.event is not None:
            lap_msg.event = (
                lap_data.event.value if isinstance(lap_data.event, Event) else lap_data.event
            )
        if hasattr(lap_data, "event_type") and lap_data.event_type is not None:
            lap_msg.event_type = (
                lap_data.event_type.value
                if isinstance(lap_data.event_type, EventType)
                else lap_data.event_type
            )

        lap_msg.total_elapsed_time = (
            lap_data.total_elapsed_time if lap_data.total_elapsed_time is not None else 0.0
        )
        lap_msg.total_timer_time = (
            lap_data.total_timer_time if lap_data.total_timer_time is not None else 0.0
        )

        if lap_data.start_position_lat is not None and lap_data.start_position_long is not None:
            lap_msg.start_position_lat = lap_data.start_position_lat
            lap_msg.start_position_long = lap_data.start_position_long
        if lap_data.end_position_lat is not None and lap_data.end_position_long is not None:
            lap_msg.end_position_lat = lap_data.end_position_lat
            lap_msg.end_position_long = lap_data.end_position_long

        if lap_data.total_distance is not None:
            lap_msg.total_distance = lap_data.total_distance

        if lap_data.avg_speed is not None:
            lap_msg.avg_speed = lap_data.avg_speed
        if lap_data.max_speed is not None:
            lap_msg.max_speed = lap_data.max_speed
        if lap_data.avg_heart_rate is not None:
            lap_msg.avg_heart_rate = lap_data.avg_heart_rate
        if lap_data.max_heart_rate is not None:
            lap_msg.max_heart_rate = lap_data.max_heart_rate
        if lap_data.avg_cadence is not None:
            lap_msg.avg_cadence = lap_data.avg_cadence
        if lap_data.max_cadence is not None:
            lap_msg.max_cadence = lap_data.max_cadence

        if lap_data.sport:
            lap_msg.sport = lap_data.sport.value
        else:
            lap_msg.sport = Sport.GENERIC.value

        return lap_msg

    def _build_session_message(
        self, session_data: SessionMessageData, index: int, all_laps_data: List[LapMessageData]
    ) -> SessionMessage:
        """Build a SessionMessage from SessionMessageData."""
        ses_msg = SessionMessage()
        ses_msg.timestamp = session_data.timestamp  # Session end time
        ses_msg.message_index = (
            session_data.message_index if session_data.message_index is not None else index
        )

        if session_data.start_time:
            ses_msg.start_time = session_data.start_time
        else:
            self.logger.warning(
                f"Session (idx {index}) missing start_time. Defaulting to session end time. This may cause issues."
            )
            ses_msg.start_time = session_data.timestamp

        ses_msg.event = Event.SESSION
        ses_msg.event_type = EventType.STOP
        if hasattr(session_data, "event") and session_data.event is not None:
            ses_msg.event = (
                session_data.event.value
                if isinstance(session_data.event, Event)
                else session_data.event
            )
        if hasattr(session_data, "event_type") and session_data.event_type is not None:
            ses_msg.event_type = (
                session_data.event_type.value
                if isinstance(session_data.event_type, EventType)
                else session_data.event_type
            )

        ses_msg.total_elapsed_time = (
            session_data.total_elapsed_time if session_data.total_elapsed_time is not None else 0.0
        )
        ses_msg.total_timer_time = (
            session_data.total_timer_time if session_data.total_timer_time is not None else 0.0
        )

        if session_data.total_distance is not None:
            ses_msg.total_distance = session_data.total_distance

        if session_data.sport:
            ses_msg.sport = session_data.sport.value
        else:
            ses_msg.sport = Sport.GENERIC.value

        if session_data.sub_sport:
            ses_msg.sub_sport = session_data.sub_sport.value

        num_laps = session_data.num_laps if session_data.num_laps is not None else 0
        first_lap_idx_val = (
            session_data.first_lap_index if session_data.first_lap_index is not None else 0
        )

        if num_laps == 0 and all_laps_data:
            session_laps = []
            for lap_idx, lap_item in enumerate(all_laps_data):
                if (
                    lap_item.start_time >= ses_msg.start_time
                    and lap_item.timestamp <= ses_msg.timestamp
                ):
                    if not session_laps:
                        first_lap_idx_val = lap_idx
                    session_laps.append(lap_item)
            num_laps = len(session_laps)
            if num_laps > 0 and session_data.first_lap_index is None:
                self.logger.info(
                    f"Session {index}: Auto-calculated first_lap_index={first_lap_idx_val}, num_laps={num_laps}"
                )

        ses_msg.first_lap_index = first_lap_idx_val
        ses_msg.num_laps = num_laps

        return ses_msg

    def write_fit_file(
        self,
        file_path: str,
        fit_file_data: LocationsFitFileData | CoursesFitFileData | ActivityFitFileData,
        data_type_hint: Optional[str] = None,
    ) -> Tuple[bool, List[str]]:
        """Write FitFileData (Locations, Courses, or Activity) to a .fit file."""
        errors = []
        builder = FitFileBuilder(auto_define=True, min_string_size=50)

        file_type_to_write = FileType.DEVICE
        actual_fit_data = None

        if isinstance(fit_file_data, LocationsFitFileData) or data_type_hint == "locations":
            file_type_to_write = FileType.LOCATIONS
            actual_fit_data = fit_file_data
            self.logger.log("Writing Locations FIT file.")
        elif isinstance(fit_file_data, CoursesFitFileData) or data_type_hint == "courses":
            file_type_to_write = FileType.COURSES
            actual_fit_data = fit_file_data
            self.logger.log("Writing Courses FIT file.")
        elif isinstance(fit_file_data, ActivityFitFileData) or data_type_hint == "activity":
            file_type_to_write = FileType.ACTIVITY
            actual_fit_data = fit_file_data
            self.logger.log("Writing Activity FIT file.")
        else:
            if hasattr(fit_file_data, "locations") and isinstance(fit_file_data.locations, list):
                file_type_to_write = FileType.LOCATIONS
                actual_fit_data = fit_file_data
                self.logger.log("Inferred and writing Locations FIT file.")
            elif hasattr(fit_file_data, "courses") and isinstance(fit_file_data.courses, list):
                file_type_to_write = FileType.COURSES
                actual_fit_data = fit_file_data
                self.logger.log("Inferred and writing Courses FIT file.")
            elif hasattr(fit_file_data, "records") and isinstance(fit_file_data.records, list):
                file_type_to_write = FileType.ACTIVITY
                actual_fit_data = fit_file_data
                self.logger.log("Inferred and writing Activity FIT file.")
            else:
                errors.append("Unsupported or ambiguous fit_file_data type for writing.")
                self.logger.error("Unsupported or ambiguous fit_file_data type for writing.")
                return False, errors

        if not hasattr(actual_fit_data, "file_id") or actual_fit_data.file_id is None:
            actual_fit_data.file_id = FileIdMessageData()
            self.logger.warning("Missing FileIdMessageData, using default.")
        if not hasattr(actual_fit_data, "creator") or actual_fit_data.creator is None:
            actual_fit_data.creator = FileCreatorMessageData()
            self.logger.warning("Missing FileCreatorMessageData, using default.")

        fid_msg = self._build_file_id_message(
            actual_fit_data.file_id, file_type_override=file_type_to_write
        )
        builder.add(fid_msg)

        if actual_fit_data.creator:
            creator_msg = self._build_file_creator_message(actual_fit_data.creator)
            builder.add(creator_msg)

        if file_type_to_write == FileType.LOCATIONS and isinstance(
            actual_fit_data, LocationsFitFileData
        ):
            if actual_fit_data.location_settings:
                ls_msg = self._build_location_settings_message(actual_fit_data.location_settings)
                builder.add(ls_msg)
            for index, wp_data_internal in enumerate(actual_fit_data.locations):
                loc_msg = self._build_location_message(index, wp_data_internal)
                if loc_msg:
                    builder.add(loc_msg)

        elif file_type_to_write == FileType.COURSES and isinstance(
            actual_fit_data, CoursesFitFileData
        ):
            for course_idx, course_data_item in enumerate(actual_fit_data.courses):
                course_msg = self._build_course_message(course_data_item, course_idx)
                builder.add(course_msg)
                for cp_idx, cp_data_item in enumerate(course_data_item.points):
                    cp_msg = self._build_course_point_message(
                        cp_data_item, cp_idx, course_msg.message_index
                    )
                    builder.add(cp_msg)

        elif file_type_to_write == FileType.ACTIVITY and isinstance(
            actual_fit_data, ActivityFitFileData
        ):
            for session_idx, session_data_item in enumerate(actual_fit_data.sessions):
                if session_data_item.num_laps == 0 and actual_fit_data.laps:
                    laps_in_this_session = [
                        lap_item
                        for lap_item in actual_fit_data.laps
                        if lap_item.start_time >= session_data_item.start_time
                        and lap_item.timestamp <= session_data_item.timestamp
                    ]
                    session_data_item.num_laps = len(laps_in_this_session)

                session_msg = self._build_session_message(
                    session_data_item, session_idx, actual_fit_data.laps
                )
                builder.add(session_msg)

            for lap_idx, lap_data_item in enumerate(actual_fit_data.laps):
                lap_msg = self._build_lap_message(lap_data_item, lap_idx)
                builder.add(lap_msg)

            for record_data_item in actual_fit_data.records:
                rec_msg = self._build_record_message(record_data_item)
                if rec_msg:
                    builder.add(rec_msg)

        if errors:
            for err in errors:
                self.logger.error(f"Critical FIT Write Error (pre-build): {err}")
            return False, errors

        try:
            fit_file_result = builder.build()
            fit_file_result.to_file(file_path)
            self.logger.log(
                f"Successfully wrote FIT file ({file_type_to_write.name}) to: {file_path}"
            )
            return True, errors

        except Exception as e:
            err_msg = f"Failed to build or write FIT file ({file_type_to_write.name}): {e}"
            self.logger.error(err_msg)
            errors.append(err_msg)
            return False, errors

    def convert_route_to_courses_fit_data(
        self,
        route_data_list: List[RouteData],
        file_id_data: Optional[FileIdMessageData] = None,
        creator_data: Optional[FileCreatorMessageData] = None,
    ) -> CoursesFitFileData:
        """Convert a list of RouteData (from tracks.py) to CoursesFitFileData."""
        courses_fit_data = CoursesFitFileData(
            file_id=file_id_data if file_id_data else FileIdMessageData(file_type=FileType.COURSES),
            creator=creator_data if creator_data else FileCreatorMessageData(),
        )

        for route_data in route_data_list:
            course_msg_data = CourseMessageData(name=route_data.name)

            for rpt_idx, rpt_data in enumerate(route_data.points):
                cp_msg_data = CoursePointMessageData(
                    name=rpt_data.name,
                    position_lat=rpt_data.latitude,
                    position_long=rpt_data.longitude,
                    type=CoursePoint.GENERIC,
                    message_index=rpt_idx,
                )
                course_msg_data.points.append(cp_msg_data)
            courses_fit_data.courses.append(course_msg_data)
        return courses_fit_data

    def convert_track_to_activity_fit_data(
        self,
        track_data_list: List[TrackData],
        file_id_data: Optional[FileIdMessageData] = None,
        creator_data: Optional[FileCreatorMessageData] = None,
    ) -> ActivityFitFileData:
        """Convert a list of TrackData (from tracks.py) to ActivityFitFileData."""
        activity_fit_data = ActivityFitFileData(
            file_id=file_id_data
            if file_id_data
            else FileIdMessageData(file_type=FileType.ACTIVITY),
            creator=creator_data if creator_data else FileCreatorMessageData(),
        )

        for track_data in track_data_list:
            all_records: List[RecordMessageData] = []
            start_time = None
            end_time = None

            for segment in track_data.segments:
                for tp_idx, tp_data in enumerate(segment.points):
                    if start_time is None and tp_data.timestamp:
                        start_time = tp_data.timestamp
                    if tp_data.timestamp:
                        end_time = tp_data.timestamp

                    record = RecordMessageData(
                        timestamp=tp_data.timestamp
                        if tp_data.timestamp
                        else datetime.now(timezone.utc),
                        position_lat=tp_data.latitude,
                        position_long=tp_data.longitude,
                        altitude=tp_data.elevation,
                    )
                    all_records.append(record)

            if not all_records:
                continue

            session_msg_data = SessionMessageData(
                start_time=start_time if start_time else all_records[0].timestamp,
                timestamp=end_time if end_time else all_records[-1].timestamp,
                total_elapsed_time=(end_time - start_time).total_seconds()
                if start_time and end_time
                else None,
                total_timer_time=(end_time - start_time).total_seconds()
                if start_time and end_time
                else None,
                sport=Sport.GENERIC,
                num_laps=1,
                first_lap_index=len(activity_fit_data.laps),
            )
            activity_fit_data.sessions.append(session_msg_data)

            lap_msg_data = LapMessageData(
                start_time=start_time if start_time else all_records[0].timestamp,
                timestamp=end_time if end_time else all_records[-1].timestamp,
                total_elapsed_time=(end_time - start_time).total_seconds()
                if start_time and end_time
                else None,
                total_timer_time=(end_time - start_time).total_seconds()
                if start_time and end_time
                else None,
            )
            activity_fit_data.laps.append(lap_msg_data)
            activity_fit_data.records.extend(all_records)

        return activity_fit_data
