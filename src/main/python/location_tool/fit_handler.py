from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, List, Optional, Tuple

import gpxpy.gpx  # For GPXXMLSyntaxException
from fit_tool.data_message import DataMessage
from fit_tool.fit_file import FitFile
from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.file_creator_message import FileCreatorMessage
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.location_message import LocationMessage
from fit_tool.profile.messages.location_settings_message import LocationSettingsMessage
from fit_tool.profile.profile_type import (
    FileType,
    GarminProduct,
    LocationSettings,
    Manufacturer,
    MapSymbol,
)
from location_tool import logging_utils

# Define conservative maximum character lengths for truncation
MAX_NAME_CHARS = 50
MAX_DESC_CHARS = 50


# --- Data Classes ---
@dataclass
class FileIdMessageData:
    file_type: Optional[FileType] = FileType.LOCATIONS  # Allow None initially if read from FIT
    manufacturer: Optional[Manufacturer] = Manufacturer.DEVELOPMENT  # Allow None initially
    product: Optional[Any] = 0  # Can be int or GarminProduct enum
    serial_number: Optional[int] = None
    time_created: Optional[datetime] = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )  # Allow None initially
    number: int = 0  # File number / part number
    product_name: Optional[str] = None  # Max 20 chars for .FIT


@dataclass
class FileCreatorMessageData:
    software_version: Optional[int] = 0  # e.g. 100 for 1.00
    hardware_version: Optional[int] = 0


@dataclass
class LocationSettingsMessageData:
    location_settings_enum: Optional[LocationSettings] = (
        None  # Stores the LocationSettings enum value
    )
    name: Optional[str] = None  # Max 16 chars for .FIT
    message_index: Optional[int] = None


@dataclass
class LocationMessageData:
    name: Optional[str] = "Waypoint"
    latitude: float = 0.0  # Degrees
    longitude: float = 0.0  # Degrees
    altitude: float = 0.0  # Meters
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    symbol: MapSymbol = MapSymbol.AIRPORT
    message_index: Optional[int] = None
    description: Optional[str] = None


@dataclass
class LocationsFitFileData:
    header: FileIdMessageData = field(default_factory=FileIdMessageData)
    creator: FileCreatorMessageData = field(default_factory=FileCreatorMessageData)
    location_settings: Optional[LocationSettingsMessageData] = None
    locations: List[LocationMessageData] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class FileHandler:
    def __init__(self, appctxt):
        self.logger = logging_utils.Logger.get_logger()
        self.appctxt = appctxt

    # --- Read Logic ---

    def read_fit_file(
        self, file_path: str, logger: Optional[Callable[[str], None]] = None
    ) -> LocationsFitFileData:
        fit_data: LocationsFitFileData = LocationsFitFileData()

        try:
            fit_file: FitFile = FitFile.from_file(file_path)
        except Exception as e:
            self.logger.error(f"Error opening or parsing FIT file: {e}")
            return fit_data

        for record_wrapper in fit_file.records:
            actual_message = record_wrapper.message

            if not isinstance(actual_message, DataMessage):
                continue

            definition_for_data: Any = (
                actual_message.definition_message
            )  # fit_tool.definition_message.DefinitionMessage
            global_id: int = definition_for_data.global_id

            try:
                # process FileIdMessage

                if global_id == FileIdMessage.ID:
                    msg: DataMessage = actual_message

                    file_type_val: Optional[int] = getattr(msg, "type", None)
                    file_type_enum: Optional[FileType] = None
                    if file_type_val is not None:
                        try:
                            file_type_enum = FileType(file_type_val)
                        except ValueError:
                            self.logger.error(
                                f"Invalid FileType value encountered: {file_type_val}"
                            )

                    manufacturer_val: Optional[int] = getattr(msg, "manufacturer", None)
                    manufacturer_enum: Optional[Manufacturer] = None
                    if manufacturer_val is not None:
                        try:
                            manufacturer_enum = Manufacturer(manufacturer_val)
                        except ValueError:
                            self.logger.error(
                                f"Invalid Manufacturer value encountered: {manufacturer_val}"
                            )

                    product_id_val: Optional[int] = getattr(msg, "product", None)
                    garmin_product_enum: Optional[GarminProduct] = None
                    if manufacturer_enum == Manufacturer.GARMIN and product_id_val is not None:
                        try:
                            garmin_product_enum = GarminProduct(product_id_val)
                        except ValueError:
                            self.logger.error(
                                f"Invalid GarminProduct value for manufacturer GARMIN: {product_id_val}"
                            )
                    elif product_id_val is not None and manufacturer_enum != Manufacturer.GARMIN:
                        pass

                    time_created: Optional[datetime] = getattr(msg, "time_created", None)

                    fit_data.header = FileIdMessageData(
                        file_type=file_type_enum,
                        manufacturer=manufacturer_enum,
                        product=garmin_product_enum if garmin_product_enum else product_id_val,
                        serial_number=getattr(msg, "serial_number", None),
                        time_created=time_created,
                        product_name=getattr(msg, "product_name", None),
                    )

                # process FileCreatorMessage
                elif global_id == FileCreatorMessage.ID:
                    msg: DataMessage = actual_message
                    fit_data.creator = FileCreatorMessageData(
                        software_version=getattr(msg, "software_version", None),
                        hardware_version=getattr(msg, "hardware_version", None),
                    )

                # process LocationSettingsMessage
                elif global_id == LocationSettingsMessage.ID:
                    msg: DataMessage = actual_message
                    # The LocationSettingsMessage has a 'location_settings' property which returns an int value
                    # that needs to be converted to a LocationSettings enum
                    location_settings_raw: Optional[int] = getattr(msg, "location_settings", None)

                    # Convert the int value to the LocationSettings enum
                    location_settings_enum: Optional[LocationSettings] = None
                    if location_settings_raw is not None:
                        try:
                            location_settings_enum = LocationSettings(location_settings_raw)
                        except ValueError:
                            self.logger.error(
                                f"Invalid LocationSettings value: {location_settings_raw}. Using None."
                            )

                    fit_data.location_settings = LocationSettingsMessageData(
                        location_settings_enum=location_settings_enum
                        # name and message_index are not directly part of this FIT message,
                        # they might be set elsewhere or based on other logic if needed.
                    )

                # process LocationMessage
                elif global_id == LocationMessage.ID:
                    msg: DataMessage = actual_message
                    lat_degrees: Optional[float] = getattr(msg, "position_lat", None)
                    lon_degrees: Optional[float] = getattr(msg, "position_long", None)
                    location_datetime_object: Optional[datetime] = getattr(msg, "timestamp", None)

                    symbol_val: Optional[int] = getattr(msg, "symbol", None)
                    symbol_enum: MapSymbol = MapSymbol.AIRPORT  # Default
                    if symbol_val is not None:
                        try:
                            symbol_enum = MapSymbol(symbol_val)
                        except ValueError:
                            self.logger.error(
                                f"Invalid MapSymbol value {symbol_val} in FIT LocationMessage. Using default."
                            )

                    waypoint: LocationMessageData = LocationMessageData(
                        name=getattr(msg, "location_name", None),
                        description=getattr(
                            msg, "description", None
                        ),  # Not standard in FIT LocationMessage but can be custom
                        latitude=lat_degrees if lat_degrees is not None else 0.0,
                        longitude=lon_degrees if lon_degrees is not None else 0.0,
                        altitude=getattr(msg, "altitude", None),
                        timestamp=location_datetime_object
                        if location_datetime_object
                        else datetime.now(timezone.utc),
                        symbol=symbol_enum,
                        message_index=getattr(msg, "message_index", None),
                    )
                    fit_data.locations.append(waypoint)
            except AttributeError as e:
                self.logger.error(
                    f"Attribute error processing message {type(actual_message).__name__} (ID: {global_id}): {e}"
                )
            except Exception as e:
                self.logger.error(
                    f"Unexpected error processing message {type(actual_message).__name__} (ID: {global_id}): {e}"
                )

        return fit_data

    def read_gpx_file(
        self, file_path: str, logger: Optional[Callable[[str], None]] = None
    ) -> Tuple[List[LocationMessageData], List[str]]:
        """
        Parses a GPX file and extracts waypoint data from <wpt> (top-level waypoints)
        and <rtept> (route points from all routes).
        Track points (<trkpt>) are ignored.
        Returns a tuple containing a list of LocationMessageData objects and a list of error/warning strings.
        """
        waypoints: List[LocationMessageData] = []
        errors: List[str] = []

        try:
            with open(file_path, "r", encoding="utf-8") as gpx_file_content:
                gpx: gpxpy.gpx.GPX = gpxpy.parse(gpx_file_content)

            # 1. Process top-level waypoints (<wpt>)
            for gpx_wp in gpx.waypoints:  # gpx_wp is gpxpy.gpx.GPXWaypoint
                timestamp: datetime
                gpx_timestamp: Optional[datetime] = gpx_wp.time
                if gpx_timestamp:
                    if gpx_timestamp.tzinfo is None:
                        timestamp = gpx_timestamp.replace(tzinfo=timezone.utc)
                    else:
                        timestamp = gpx_timestamp.astimezone(timezone.utc)
                else:
                    timestamp = datetime.now(timezone.utc)

                symbol_to_assign: MapSymbol = MapSymbol.AIRPORT  # Default from LocationMessageData
                if gpx_wp.symbol:
                    try:
                        sym_str: str = gpx_wp.symbol.strip().upper().replace(" ", "_")
                        if sym_str in MapSymbol.__members__:
                            symbol_to_assign = MapSymbol[sym_str]
                        else:
                            try:
                                sym_int: int = int(gpx_wp.symbol)
                                symbol_to_assign = MapSymbol(
                                    sym_int
                                )  # Raises ValueError if invalid
                            except ValueError:
                                err_msg: str = f"GPX waypoint symbol '{gpx_wp.symbol}' is not a recognized MapSymbol name or integer value. Using default."
                                self.logger.error(err_msg)
                                errors.append(err_msg)
                    except Exception as e:
                        err_msg: str = f"Could not map GPX waypoint symbol '{gpx_wp.symbol}' to FIT symbol: {e}. Using default."
                        self.logger.error(err_msg)
                        errors.append(err_msg)

                altitude: Optional[float] = gpx_wp.elevation

                description: Optional[str] = gpx_wp.description
                if not description and hasattr(gpx_wp, "comment") and gpx_wp.comment:
                    description = gpx_wp.comment
                elif not description and hasattr(gpx_wp, "cmt") and gpx_wp.cmt:
                    description = gpx_wp.cmt

                name: str = gpx_wp.name or "Waypoint"

                if gpx_wp.latitude is None or gpx_wp.longitude is None:
                    errors.append(f"Skipping waypoint '{name}' due to missing latitude/longitude.")
                    continue

                wp: LocationMessageData = LocationMessageData(
                    name=name,
                    description=description,
                    latitude=gpx_wp.latitude,
                    longitude=gpx_wp.longitude,
                    altitude=altitude,
                    timestamp=timestamp,
                    symbol=symbol_to_assign,
                    message_index=len(waypoints),
                )
                waypoints.append(wp)

            if (
                not waypoints and not errors
            ):  # Only log if no points found AND no other errors occurred
                info_msg: str = (
                    "GPX file parsed, but no waypoints or route points were found or extracted."
                )
                self.logger.log(info_msg)
                # errors.append(info_msg) # Appending to errors might be too strong for just an empty file.

        except gpxpy.gpx.GPXXMLSyntaxException as e:
            err_msg: str = f"Error parsing GPX XML in file '{file_path}': {e}"
            self.logger.error(err_msg)
            errors.append(err_msg)
        except Exception as e:
            # Catch any other unexpected error during GPX processing
            err_msg: str = f"Unexpected error processing GPX file '{file_path}': {e}"
            self.logger.error(err_msg)
            errors.append(err_msg)

        return waypoints, errors

    # --- Write Logic ---

    def _prepare_file_id_message(self, header):
        fid_msg = FileIdMessage()

        fid_msg.type = header.file_type if header.file_type is not None else FileType.LOCATIONS
        fid_msg.manufacturer = (
            header.manufacturer if header.manufacturer is not None else Manufacturer.DEVELOPMENT
        )
        if header.product is not None:
            # Check if product is an enum (like GarminProduct) or a raw int
            if isinstance(header.product, GarminProduct):
                fid_msg.product = header.product.value
            else:
                fid_msg.product = header.product
        else:
            # Default product ID, aligns with FileIdMessageData default if manufacturer is DEVELOPMENT
            fid_msg.product = 0 if header.manufacturer == Manufacturer.DEVELOPMENT else 1

        fid_msg.serial_number = header.serial_number if header.serial_number is not None else 0
        fid_msg.time_created = (
            header.time_created if header.time_created is not None else datetime.now(timezone.utc)
        )
        if header.product_name is not None:
            fid_msg.product_name = header.product_name
        # No else needed here, if product_name is None, it remains unset in fid_msg

        return fid_msg

    def _prepare_file_creator_message(self, creator):
        creator_msg: FileCreatorMessage = FileCreatorMessage()
        creator_msg.software_version = (
            creator.software_version if creator.software_version is not None else 0
        )
        creator_msg.hardware_version = (
            creator.hardware_version if creator.hardware_version is not None else 0
        )
        return creator_msg

    def _prepare_location_settings_message(self, location_settings):
        ls_msg: LocationSettingsMessage = LocationSettingsMessage()
        # enum to int
        ls_msg.location_settings = location_settings.location_settings_enum.value
        return ls_msg

    def _prepare_location_message(self, index, wp_data):
        loc_msg: LocationMessage = LocationMessage()

        if wp_data.name and len(wp_data.name) > MAX_NAME_CHARS:
            self.logger.warning(
                f"Warning: Waypoint {wp_data.name} name truncated to ({MAX_NAME_CHARS} chars limit)."
            )

        if wp_data.description and len(wp_data.description) > MAX_DESC_CHARS:
            self.logger.warning(
                f"Warning: Waypoint {wp_data.name} description truncated to ({MAX_DESC_CHARS} chars limit)."
            )

        loc_msg.location_name = wp_data.name[:MAX_NAME_CHARS] if wp_data.name else "Waypoint"
        loc_msg.description = wp_data.description[:MAX_DESC_CHARS] if wp_data.description else None

        if wp_data.latitude is not None and wp_data.longitude is not None:
            loc_msg.position_lat = wp_data.latitude
            loc_msg.position_long = wp_data.longitude
        else:
            # errors.append(
            #     f"Waypoint '{wp_data.name or f'index: {index}'}' skipped due to missing latitude/longitude."
            # )
            return None

        if wp_data.altitude is not None:
            loc_msg.altitude = wp_data.altitude

        loc_msg.timestamp = wp_data.timestamp if wp_data.timestamp else datetime.now(timezone.utc)

        if isinstance(wp_data.symbol, MapSymbol):
            loc_msg.symbol = wp_data.symbol.value
        elif isinstance(wp_data.symbol, int):
            try:
                MapSymbol(wp_data.symbol)
                loc_msg.symbol = wp_data.symbol
            except ValueError:
                # warnings.append(
                #     f"Waypoint '{wp_data.name}' had an invalid integer symbol '{wp_data.symbol}'. Defaulted to FLAG_BLUE."
                # )
                loc_msg.symbol = MapSymbol.FLAG_BLUE.value
        else:
            # warnings.append(
            #     f"Waypoint '{wp_data.name}' had an invalid symbol type '{type(wp_data.symbol)}'. Defaulted to FLAG_BLUE."
            # )
            loc_msg.symbol = MapSymbol.FLAG_BLUE.value

        loc_msg.message_index = (
            wp_data.message_index if wp_data.message_index is not None else index
        )

        return loc_msg

    def write_fit_file(
        self, file_path: str, fit_data: LocationsFitFileData
    ) -> Tuple[bool, List[str], List[str]]:
        """Writes the provided LocationsFitFileData to a .fit file."""

        warnings: List[str] = []
        errors: List[str] = []
        builder: FitFileBuilder = FitFileBuilder(auto_define=True, min_string_size=50)

        # ============================================================
        # ===================== File ID Message ======================
        # ============================================================

        fid_msg: FileIdMessage = self._prepare_file_id_message(fit_data.header)
        builder.add(fid_msg)

        # ============================================================
        # =================== File Creator Message ===================
        # ============================================================
        creator_msg: FileCreatorMessage = self._prepare_file_creator_message(fit_data.creator)
        builder.add(creator_msg)

        # ============================================================
        # =================== Location Settings Message ==============
        # ============================================================
        ls_msg: LocationSettingsMessage = self._prepare_location_settings_message(
            fit_data.location_settings
        )
        builder.add(ls_msg)

        # ============================================================
        # ===================== Location Messages ====================
        # ============================================================
        for index, wp_data in enumerate(fit_data.locations):
            loc_msg = self._prepare_location_message(index, wp_data)
            if loc_msg:
                builder.add(loc_msg)

        if errors:
            for err in errors:
                self.logger.error(f"Critical FIT Write Error: {err}")
            return False, warnings, errors

        try:
            fit_file_result: FitFile = builder.build()
            fit_file_result.to_file(file_path)
            self.logger.log(f"Successfully wrote FIT file to: {file_path}")
            return True, warnings, errors

        except Exception as e:
            err_msg: str = f"Failed to build or write FIT file: {e}"
            self.logger.error(err_msg)
            errors.append(err_msg)
            return False, warnings, errors
