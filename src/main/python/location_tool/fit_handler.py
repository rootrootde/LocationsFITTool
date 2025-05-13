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

from .utils import process_raw_timestamp

# Define conservative maximum character lengths for truncation
MAX_NAME_CHARS = 50
MAX_DESC_CHARS = 50


# --- Data Classes ---
@dataclass
class FitHeaderData:
    file_type: FileType = FileType.LOCATIONS
    manufacturer: Manufacturer = Manufacturer.DEVELOPMENT
    product: int = 0  # Generic product ID
    serial_number: Optional[int] = None
    time_created: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    number: int = 0  # File number / part number
    product_name: Optional[str] = None  # Max 20 chars for .FIT


@dataclass
class FitCreatorData:
    software_version: int = 0  # e.g. 100 for 1.00
    hardware_version: int = 0


@dataclass
class FitLocationSettingData:
    location_settings_enum: Optional[LocationSettings] = (
        None  # Stores the LocationSettings enum value
    )
    name: Optional[str] = None  # Max 16 chars for .FIT
    message_index: Optional[int] = None


@dataclass
class FitLocationData:
    name: Optional[str] = "Waypoint"
    latitude: float = 0.0  # Degrees
    longitude: float = 0.0  # Degrees
    altitude: float = 0.0  # Meters
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    symbol: MapSymbol = MapSymbol.AIRPORT  # Changed from GENERIC
    message_index: Optional[int] = None
    description: Optional[str] = None  # For internal/GPX use


@dataclass
class LocationsFitFileData:
    header: FitHeaderData = field(default_factory=FitHeaderData)
    creator: FitCreatorData = field(default_factory=FitCreatorData)
    location_settings: Optional[FitLocationSettingData] = None
    locations: List[FitLocationData] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


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
                processed_time_created = process_raw_timestamp(
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
                # The LocationSettingsMessage has a 'location_settings' property which returns the LocationSettings enum
                location_settings_value = getattr(msg, "location_settings", None)

                # Ensure it's the correct enum type if a value is present
                if location_settings_value is not None and not isinstance(
                    location_settings_value, LocationSettings
                ):
                    if logger:
                        logger(
                            f"Warning: LocationSettingsMessage.location_settings was not of type LocationSettings enum, but {type(location_settings_value)}. Value: {location_settings_value}"
                        )
                    location_settings_value = (
                        None  # Or attempt conversion if appropriate and safe
                    )

                fit_data.location_settings = FitLocationSettingData(
                    location_settings_enum=location_settings_value
                    # name and message_index are not directly part of this FIT message,
                    # they might be set elsewhere or based on other logic if needed.
                )

            # process LocationMessage
            elif global_id == LocationMessage.ID:
                msg = actual_message
                lat_degrees = getattr(msg, "position_lat", None)
                lon_degrees = getattr(msg, "position_long", None)

                raw_location_timestamp = getattr(msg, "timestamp", None)
                location_datetime_object = process_raw_timestamp(
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
                fit_data.locations.append(waypoint)
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


def read_gpx_file(
    file_path: str, logger=None
) -> tuple[List[FitLocationData], List[str]]:
    """
    Parses a GPX file and extracts waypoint data from <wpt> (top-level waypoints)
    and <rtept> (route points from all routes).
    Track points (<trkpt>) are ignored.
    Returns a tuple containing a list of FitLocationData objects and a list of error/warning strings.
    """
    waypoints: List[FitLocationData] = []
    errors: List[str] = []

    try:
        # Import gpxpy locally to make the ImportError exception more specific
        # and to handle the case where gpxpy is not installed.
        import gpxpy.gpx  # For GPXXMLSyntaxException
    except ImportError:
        err_msg = "GPX parsing requires the 'gpxpy' library. Please install it: pip install gpxpy"
        if logger:
            logger(err_msg)
        errors.append(err_msg)
        return waypoints, errors  # Return early if gpxpy is not available

    try:
        with open(file_path, "r", encoding="utf-8") as gpx_file_content:
            gpx = gpxpy.parse(gpx_file_content)

        # 1. Process top-level waypoints (<wpt>)
        for gpx_wp in gpx.waypoints:
            timestamp = gpx_wp.time
            if timestamp:
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                else:
                    timestamp = timestamp.astimezone(timezone.utc)
            else:
                timestamp = datetime.now(timezone.utc)

            symbol_to_assign = MapSymbol.AIRPORT  # Default from FitLocationData
            if gpx_wp.symbol:
                try:
                    sym_str = gpx_wp.symbol.strip().upper().replace(" ", "_")
                    if sym_str in MapSymbol.__members__:
                        symbol_to_assign = MapSymbol[sym_str]
                    else:
                        try:
                            sym_int = int(gpx_wp.symbol)
                            symbol_to_assign = MapSymbol(
                                sym_int
                            )  # Raises ValueError if invalid
                        except ValueError:
                            err_msg = f"GPX waypoint symbol '{gpx_wp.symbol}' is not a recognized MapSymbol name or integer value. Using default."
                            if logger:
                                logger(err_msg)
                            errors.append(err_msg)
                except Exception as e:
                    err_msg = f"Could not map GPX waypoint symbol '{gpx_wp.symbol}' to FIT symbol: {e}. Using default."
                    if logger:
                        logger(err_msg)
                    errors.append(err_msg)

            altitude = gpx_wp.elevation

            description = gpx_wp.description
            if not description and hasattr(gpx_wp, "comment") and gpx_wp.comment:
                description = gpx_wp.comment
            elif not description and hasattr(gpx_wp, "cmt") and gpx_wp.cmt:
                description = gpx_wp.cmt

            name = gpx_wp.name or "Waypoint"

            if gpx_wp.latitude is None or gpx_wp.longitude is None:
                errors.append(
                    f"Skipping waypoint '{name}' due to missing latitude/longitude."
                )
                continue

            wp = FitLocationData(
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

        # 2. Process points from all routes (<rtept> within <rte>)
        if gpx.routes:
            for route_idx, route in enumerate(gpx.routes):
                route_name_prefix = route.name or f"Route {route_idx + 1}"
                if route.points:
                    for point_idx, route_pt in enumerate(route.points):
                        timestamp = route_pt.time
                        if timestamp:
                            if timestamp.tzinfo is None:
                                timestamp = timestamp.replace(tzinfo=timezone.utc)
                            else:
                                timestamp = timestamp.astimezone(timezone.utc)
                        else:
                            timestamp = datetime.now(timezone.utc)

                        symbol_to_assign = MapSymbol.AIRPORT  # Default
                        if route_pt.symbol:
                            try:
                                sym_str = (
                                    route_pt.symbol.strip().upper().replace(" ", "_")
                                )
                                if sym_str in MapSymbol.__members__:
                                    symbol_to_assign = MapSymbol[sym_str]
                                else:
                                    try:
                                        sym_int = int(route_pt.symbol)
                                        symbol_to_assign = MapSymbol(
                                            sym_int
                                        )  # Raises ValueError if invalid
                                    except ValueError:
                                        err_msg = f"GPX route point symbol '{route_pt.symbol}' is not a recognized MapSymbol name or integer value. Using default."
                                        if logger:
                                            logger(err_msg)
                                        errors.append(err_msg)
                            except Exception as e:
                                err_msg = f"Could not map GPX route point symbol '{route_pt.symbol}' to FIT symbol: {e}. Using default."
                                if logger:
                                    logger(err_msg)
                                errors.append(err_msg)

                        altitude = route_pt.elevation

                        description = route_pt.description
                        if (
                            not description
                            and hasattr(route_pt, "comment")
                            and route_pt.comment
                        ):
                            description = route_pt.comment
                        # GPXRoutePoint does not have .cmt attribute

                        name = (
                            route_pt.name
                            or f"{route_name_prefix} - Point {point_idx + 1}"
                        )

                        if route_pt.latitude is None or route_pt.longitude is None:
                            errors.append(
                                f"Skipping route point '{name}' due to missing latitude/longitude."
                            )
                            continue

                        wp = FitLocationData(
                            name=name,
                            description=description,
                            latitude=route_pt.latitude,
                            longitude=route_pt.longitude,
                            altitude=altitude,
                            timestamp=timestamp,
                            symbol=symbol_to_assign,
                            message_index=len(waypoints),
                        )
                        waypoints.append(wp)

        # 3. Track points are intentionally not processed.

        if (
            not waypoints and not errors
        ):  # Only log if no points found AND no other errors occurred
            info_msg = "GPX file parsed, but no waypoints or route points were found or extracted."
            if logger:
                logger(info_msg)
            # errors.append(info_msg) # Appending to errors might be too strong for just an empty file.

    except gpxpy.gpx.GPXXMLSyntaxException as e:
        err_msg = f"Error parsing GPX XML in file '{file_path}': {e}"
        if logger:
            logger(err_msg)
        errors.append(err_msg)
    except Exception as e:
        # Catch any other unexpected error during GPX processing
        err_msg = f"Unexpected error processing GPX file '{file_path}': {e}"
        if logger:
            logger(err_msg)
            # For debugging, you might want to log the traceback:
            # import traceback
            # logger(traceback.format_exc())
        errors.append(err_msg)

    return waypoints, errors


# --- Write Logic ---


def write_fit_file(
    file_path: str, fit_data: LocationsFitFileData, logger=None
) -> tuple[bool, List[str], List[str]]:
    """Writes the provided LocationsFitFileData to a .fit file.
    Returns a tuple of (success_status, warnings, critical_errors).
    """
    warnings: List[str] = []
    critical_errors: List[str] = []
    builder = FitFileBuilder(auto_define=True, min_string_size=50)

    # File ID Message
    fid_msg = FileIdMessage()
    # fit_data.header will always exist due to default_factory=FitHeaderData
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
        # Check if product is an enum (like GarminProduct) or a raw int
        if isinstance(header.product, GarminProduct):
            fid_msg.product = header.product.value
        else:
            fid_msg.product = header.product
    else:
        # Default product ID, aligns with FitHeaderData default if manufacturer is DEVELOPMENT
        fid_msg.product = 0 if header.manufacturer == Manufacturer.DEVELOPMENT else 1

    fid_msg.serial_number = (
        header.serial_number if header.serial_number is not None else 0
    )
    fid_msg.time_created = (
        header.time_created
        if header.time_created is not None
        else datetime.now(timezone.utc)
    )
    if (
        header.product_name is not None
    ):  # Max 20 chars for .FIT, handled by fit_tool library
        fid_msg.product_name = header.product_name
    # No else needed here, if product_name is None, it remains unset in fid_msg
    builder.add(fid_msg)

    # File Creator Message
    creator_msg = FileCreatorMessage()
    # fit_data.creator will always exist due to default_factory=FitCreatorData
    creator = fit_data.creator
    creator_msg.software_version = (
        creator.software_version if creator.software_version is not None else 0
    )
    creator_msg.hardware_version = (
        creator.hardware_version if creator.hardware_version is not None else 0
    )
    builder.add(creator_msg)

    # Location Settings Message
    ls_msg = LocationSettingsMessage()
    if (
        fit_data.location_settings
        and fit_data.location_settings.location_settings_enum is not None
    ):
        ls_msg.location_settings = fit_data.location_settings.location_settings_enum
    else:
        ls_msg.location_settings = LocationSettings.ADD  # Defaulting to ADD
        warnings.append(
            "Info: Location Settings data was missing or invalid; a default setting (ADD) was applied."
        )
    builder.add(ls_msg)

    # Location Messages (Waypoints)
    for index, wp_data in enumerate(fit_data.locations):
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
        return True, warnings, critical_errors  # Return True on success
    except Exception as e:
        critical_errors.append(f"Error building or writing FIT file: {e}")
        if logger:
            logger(f"Error building or writing FIT file: {e}")
        return False, warnings, critical_errors  # Return False on failure
