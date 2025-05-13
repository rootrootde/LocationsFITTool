from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

import gpxpy
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

# Define conservative maximum character lengths for truncation
MAX_NAME_CHARS = 50
MAX_DESC_CHARS = 50


# --- Data Classes ---
@dataclass
class FitHeaderData:
    file_type: Optional[FileType] = None
    manufacturer: Optional[Manufacturer] = None
    product: Optional[GarminProduct] = None
    serial_number: Optional[int] = None
    time_created: Optional[datetime] = None
    product_name: Optional[str] = None


@dataclass
class FitCreatorData:
    software_version: Optional[int] = None
    hardware_version: Optional[int] = None


@dataclass
class FitLocationSettingData:  # Renamed from FitWaypointSettingData
    waypoint_setting: Optional[LocationSettings] = None


@dataclass
class FitLocationData:
    name: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    timestamp: Optional[datetime] = None
    symbol: Optional[int] = None
    message_index: Optional[int] = None


@dataclass
class LocationsFitFileData:
    header: Optional[FitHeaderData] = None
    creator: Optional[FitCreatorData] = None
    settings: Optional[FitLocationSettingData] = None
    waypoints: List[FitLocationData] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


# --- Helper Function for Timestamp Processing ---
def _process_raw_timestamp(raw_timestamp: any, logger=None) -> Optional[datetime]:
    """
    Converts a raw timestamp value to a timezone-aware UTC datetime object.
    The raw_timestamp can be an int/float (assumed ms since Unix epoch)
    or a datetime object.
    """
    if raw_timestamp is None:
        return None

    processed_dt = None
    if isinstance(raw_timestamp, (int, float)):
        try:
            processed_dt = datetime.fromtimestamp(
                raw_timestamp / 1000.0, tz=timezone.utc
            )
        except Exception as e:
            if logger:
                logger(f"Error converting timestamp ({raw_timestamp}) to datetime: {e}")
    elif isinstance(raw_timestamp, datetime):
        processed_dt = raw_timestamp
        if processed_dt.tzinfo is None:
            processed_dt = processed_dt.replace(tzinfo=timezone.utc)
        else:
            processed_dt = processed_dt.astimezone(timezone.utc)
    else:
        if logger:
            logger(
                f"Unexpected type for timestamp: {type(raw_timestamp)}. Value: {raw_timestamp}"
            )
    return processed_dt


# --- Read Logic ---
def read_fit_file(file_path: str, logger=None) -> LocationsFitFileData:
    fit_data = LocationsFitFileData()

    try:
        fit_file = FitFile.from_file(file_path)
    except Exception as e:
        if logger:
            logger(f"Error opening or parsing FIT file: {e}")
        return fit_data

    for record_wrapper in fit_file.records:
        actual_message = record_wrapper.message

        if not isinstance(actual_message, DataMessage):
            continue

        definition_for_data = actual_message.definition_message
        global_id = definition_for_data.global_id

        try:
            # process FileIdMessage

            if global_id == FileIdMessage.ID:
                msg = actual_message

                file_type_val = getattr(msg, "type", None)
                file_type_enum = None
                if file_type_val is not None:
                    try:
                        file_type_enum = FileType(file_type_val)
                    except ValueError:
                        if logger:
                            logger(
                                f"Invalid FileType value encountered: {file_type_val}"
                            )

                manufacturer_val = getattr(msg, "manufacturer", None)
                manufacturer_enum = None
                if manufacturer_val is not None:
                    try:
                        manufacturer_enum = Manufacturer(manufacturer_val)
                    except ValueError:
                        if logger:
                            logger(
                                f"Invalid Manufacturer value encountered: {manufacturer_val}"
                            )

                product_id_val = getattr(msg, "product", None)
                garmin_product_enum = None
                if (
                    manufacturer_enum == Manufacturer.GARMIN
                    and product_id_val is not None
                ):
                    try:
                        garmin_product_enum = GarminProduct(product_id_val)
                    except ValueError:
                        if logger:
                            logger(
                                f"Invalid GarminProduct value for manufacturer GARMIN: {product_id_val}"
                            )
                elif (
                    product_id_val is not None
                    and manufacturer_enum != Manufacturer.GARMIN
                ):
                    pass

                time_created_val = getattr(msg, "time_created", None)
                processed_time_created = _process_raw_timestamp(
                    time_created_val, logger=logger
                )

                fit_data.header = FitHeaderData(
                    file_type=file_type_enum,
                    manufacturer=manufacturer_enum,
                    product=garmin_product_enum,
                    serial_number=getattr(msg, "serial_number", None),
                    time_created=processed_time_created,
                    product_name=getattr(msg, "product_name", None),
                )

            # process FileCreatorMessage
            elif global_id == FileCreatorMessage.ID:
                msg = actual_message
                fit_data.creator = FitCreatorData(
                    software_version=getattr(msg, "software_version", None),
                    hardware_version=getattr(msg, "hardware_version", None),
                )

            # process LocationSettingsMessage
            elif global_id == LocationSettingsMessage.ID:
                msg = actual_message
                setting_val = getattr(msg, "location_settings", None)
                setting_enum = None
                if setting_val is not None:
                    try:
                        setting_enum = LocationSettings(setting_val)
                    except ValueError:
                        if logger:
                            logger(
                                f"Invalid LocationSetting value encountered: {setting_val}"
                            )
                fit_data.settings = FitLocationSettingData(
                    waypoint_setting=setting_enum
                )

            # process LocationMessage
            elif global_id == LocationMessage.ID:
                msg = actual_message
                lat_degrees = getattr(msg, "position_lat", None)
                lon_degrees = getattr(msg, "position_long", None)

                raw_location_timestamp = getattr(msg, "timestamp", None)
                location_datetime_object = _process_raw_timestamp(
                    raw_location_timestamp, logger=logger
                )

                waypoint = FitLocationData(
                    name=getattr(msg, "location_name", None),
                    description=getattr(msg, "description", None),
                    latitude=lat_degrees,
                    longitude=lon_degrees,
                    altitude=getattr(msg, "altitude", None),
                    timestamp=location_datetime_object,
                    symbol=getattr(msg, "symbol", None),
                    message_index=getattr(msg, "message_index", None),
                )
                fit_data.waypoints.append(waypoint)
        except AttributeError as e:
            if logger:
                logger(
                    f"Attribute error processing message {type(actual_message).__name__} (ID: {global_id}): {e}"
                )
        except Exception as e:
            if logger:
                logger(
                    f"Unexpected error processing message {type(actual_message).__name__} (ID: {global_id}): {e}"
                )

    return fit_data


def read_gpx_file(file_path: str, logger=None) -> List[FitLocationData]:
    """
    Parses a GPX file and extracts waypoint data.
    """
    waypoints: List[FitLocationData] = []
    try:
        with open(file_path, "r", encoding="utf-8") as gpx_file_content:
            gpx = gpxpy.parse(gpx_file_content)

        for idx, gpx_wp in enumerate(gpx.waypoints):
            timestamp = gpx_wp.time
            if timestamp:
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                else:
                    timestamp = timestamp.astimezone(timezone.utc)
            else:
                # If GPX waypoint has no timestamp, use current time or handle as needed
                timestamp = datetime.now(timezone.utc)

            # Try to get a symbol, often from <sym> tag in GPX
            # GPX symbols are strings, FIT symbols are integers. Mapping might be needed.
            # For now, using a default if not found or not an integer.
            symbol_val = 0  # Default FIT symbol
            if gpx_wp.symbol:
                try:
                    # Use MapSymbol Enum for mapping GPX sym tag to FIT symbol integer
                    sym_str = gpx_wp.symbol.upper()
                    if sym_str in MapSymbol.__members__:
                        symbol_val = MapSymbol[sym_str].value
                except Exception:
                    if logger:
                        logger(
                            f"Could not map GPX symbol '{gpx_wp.symbol}' to FIT symbol."
                        )

            # Altitude (elevation in GPX)
            altitude = gpx_wp.elevation

            # Use comment/cmt as description if description is empty
            description = gpx_wp.description
            if not description and hasattr(gpx_wp, "comment") and gpx_wp.comment:
                description = gpx_wp.comment
            elif not description and hasattr(gpx_wp, "cmt") and gpx_wp.cmt:
                description = gpx_wp.cmt

            wp = FitLocationData(
                name=gpx_wp.name,
                description=description,
                latitude=gpx_wp.latitude,
                longitude=gpx_wp.longitude,
                altitude=altitude,
                timestamp=timestamp,
                symbol=symbol_val,
                message_index=idx,  # This will be re-indexed by the GUI later when appending
            )
            waypoints.append(wp)

        if not waypoints and gpx.routes:
            # Fallback: if no waypoints, try to get points from the first route
            for route_idx, route_pt in enumerate(gpx.routes[0].points):
                timestamp = route_pt.time
                if timestamp:
                    if timestamp.tzinfo is None:
                        timestamp = timestamp.replace(tzinfo=timezone.utc)
                    else:
                        timestamp = timestamp.astimezone(timezone.utc)
                else:
                    timestamp = datetime.now(timezone.utc)

                altitude = route_pt.elevation

                wp = FitLocationData(
                    name=route_pt.name or f"RoutePt {route_idx}",
                    description=route_pt.comment,
                    latitude=route_pt.latitude,
                    longitude=route_pt.longitude,
                    altitude=altitude,
                    timestamp=timestamp,
                    symbol=0,  # Default symbol for route points
                    message_index=idx + 1 + route_idx,  # Continue indexing
                )
                waypoints.append(wp)

    except ImportError:
        # This error should ideally be caught by the GUI and inform the user
        if logger:
            logger(
                "GPX parsing requires the 'gpxpy' library. Please install it: pip install gpxpy"
            )
        return waypoints
    except Exception as e:
        # Log or raise a more specific error to be handled by the GUI
        if logger:
            logger(f"Error parsing GPX file {file_path}: {e}")
        return waypoints

    return waypoints


# --- Write Logic ---
def get_timestamp_from_datetime(dt: Optional[datetime]) -> Optional[int]:
    """Converts an optional datetime object to an integer timestamp in milliseconds since UTC epoch."""
    if dt is None:
        return None
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return round(dt.timestamp() * 1000)


def degrees_to_semicircles(degrees: Optional[float]) -> Optional[int]:
    """Converts degrees to semicircles."""
    if degrees is None:
        return None
    return round(degrees * (2**31 / 180.0))


def write_fit_file(
    file_path: str, fit_data: LocationsFitFileData, logger=None
) -> tuple[List[str], List[str]]:
    """Writes the provided LocationsFitFileData to a .fit file.
    Returns a tuple of (warnings, critical_errors).
    """
    warnings: List[str] = []
    critical_errors: List[str] = []
    builder = FitFileBuilder(auto_define=True, min_string_size=50)

    # File ID Message
    fid_msg = FileIdMessage()
    if fit_data.header:
        header = fit_data.header
        fid_msg.type = (
            header.file_type if header.file_type is not None else FileType.LOCATIONS
        )
        fid_msg.manufacturer = (
            header.manufacturer
            if header.manufacturer is not None
            else Manufacturer.DEVELOPMENT
        )
        if header.product is not None:
            if isinstance(header.product, GarminProduct):
                fid_msg.product = header.product.value
            else:
                fid_msg.product = header.product
        else:
            fid_msg.product = 1  # Default product ID for Development manufacturer
        fid_msg.serial_number = (
            header.serial_number if header.serial_number is not None else 0
        )
        fid_msg.time_created = (
            header.time_created
            if header.time_created is not None
            else datetime.now(timezone.utc)
        )
        if header.product_name is not None:
            fid_msg.product_name = header.product_name
    else:
        # Hardcoded defaults for FileIdMessage if no header info from GUI/import
        fid_msg.type = FileType.LOCATIONS
        fid_msg.manufacturer = Manufacturer.DEVELOPMENT
        fid_msg.product = 1  # Example product ID for Development
        fid_msg.serial_number = 0
        fid_msg.time_created = datetime.now(timezone.utc)
        # fid_msg.product_name = "LocationsTool"  # Optional default product name
    builder.add(fid_msg)

    # File Creator Message
    creator_msg = FileCreatorMessage()
    if fit_data.creator:
        creator = fit_data.creator
        creator_msg.software_version = (
            creator.software_version if creator.software_version is not None else 1
        )
        creator_msg.hardware_version = (
            creator.hardware_version if creator.hardware_version is not None else 1
        )
    else:
        # Hardcoded defaults for FileCreatorMessage
        creator_msg.software_version = 1
        creator_msg.hardware_version = 1
    builder.add(creator_msg)

    # Location Settings Message
    ls_msg = LocationSettingsMessage()
    if fit_data.settings and fit_data.settings.waypoint_setting is not None:
        ls_msg.location_settings = fit_data.settings.waypoint_setting
    else:
        # Default LocationSettings if not provided (e.g., new file from scratch)
        ls_msg.location_settings = LocationSettings.ADD  # Defaulting to ADD
        warnings.append(
            "Info: Location Settings data was missing; a default setting (ADD) was applied."
        )
    builder.add(ls_msg)

    # Location Messages (Waypoints)
    for index, wp_data in enumerate(fit_data.waypoints):
        loc_msg = LocationMessage()

        # Truncate name and description based on estimated byte length
        name_to_set = wp_data.name
        if name_to_set is not None:
            name_bytes = name_to_set.encode("utf-8")
            if (
                len(name_bytes) > MAX_NAME_CHARS
            ):  # Assuming MAX_NAME_CHARS is now a byte limit
                # Truncate byte string and decode back, ignoring errors during decode
                name_bytes = name_bytes[:MAX_NAME_CHARS]
                name_to_set = name_bytes.decode("utf-8", "ignore")
                warnings.append(
                    f"Warning: Waypoint {index} name truncated to fit byte limit (approx. {MAX_NAME_CHARS} bytes)."
                )
        loc_msg.location_name = name_to_set

        desc_to_set = wp_data.description
        if desc_to_set is not None:
            desc_bytes = desc_to_set.encode("utf-8")
            if (
                len(desc_bytes) > MAX_DESC_CHARS
            ):  # Assuming MAX_DESC_CHARS is now a byte limit
                desc_bytes = desc_bytes[:MAX_DESC_CHARS]
                desc_to_set = desc_bytes.decode("utf-8", "ignore")
                warnings.append(
                    f"Warning: Waypoint {index} description truncated to fit byte limit (approx. {MAX_DESC_CHARS} bytes)."
                )
        loc_msg.description = desc_to_set

        if wp_data.latitude is not None:
            loc_msg.position_lat = wp_data.latitude  # Already in degrees
        if wp_data.longitude is not None:
            loc_msg.position_long = wp_data.longitude  # Already in degrees
        if wp_data.altitude is not None:
            loc_msg.altitude = wp_data.altitude
        if wp_data.timestamp is not None:
            loc_msg.timestamp = wp_data.timestamp  # Pass datetime object
        if wp_data.symbol is not None:
            loc_msg.symbol = wp_data.symbol
        # Ensure message_index is set, defaulting to loop index if not present
        loc_msg.message_index = (
            wp_data.message_index if wp_data.message_index is not None else index
        )
        builder.add(loc_msg)

    try:
        fit_file_built = builder.build()
        fit_file_built.to_file(file_path)
    except Exception as e:
        critical_errors.append(f"Error building or writing FIT file: {e}")
        if logger:
            logger(f"Error building or writing FIT file: {e}")

    return warnings, critical_errors
