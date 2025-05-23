from datetime import datetime, timezone
from typing import Callable, List, Optional, Tuple

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

from . import logger
from .fit_data import (
    FileCreatorMessageData,
    FileIdMessageData,
    LocationSettingsMessageData,
    LocationsFitFileData,
)
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
    ) -> LocationsFitFileData:
        """Parse a FIT file and return LocationsFitFileData."""
        fit_data = LocationsFitFileData()
        parsed_waypoints = []

        try:
            fit_file = FitFile.from_file(file_path)
        except Exception as e:
            self.logger.error(f"Error opening or parsing FIT file: {e}")
            return fit_data

        for record_wrapper in fit_file.records:
            actual_message = record_wrapper.message

            if not isinstance(actual_message, DataMessage):
                continue

            global_id = actual_message.definition_message.global_id

            try:
                if global_id == FileIdMessage.ID:
                    msg = actual_message

                    file_type_val = getattr(msg, "type", None)
                    file_type_enum = None
                    if file_type_val is not None:
                        try:
                            file_type_enum = FileType(file_type_val)
                        except ValueError:
                            self.logger.error(
                                f"Invalid FileType value encountered: {file_type_val}"
                            )

                    manufacturer_val = getattr(msg, "manufacturer", None)
                    manufacturer_enum = None
                    if manufacturer_val is not None:
                        try:
                            manufacturer_enum = Manufacturer(manufacturer_val)
                        except ValueError:
                            self.logger.error(
                                f"Invalid Manufacturer value encountered: {manufacturer_val}"
                            )

                    product_id_val = getattr(msg, "product", None)
                    garmin_product_enum = None
                    if manufacturer_enum == Manufacturer.GARMIN and product_id_val is not None:
                        try:
                            garmin_product_enum = GarminProduct(product_id_val)
                        except ValueError:
                            self.logger.error(
                                f"Invalid GarminProduct value for manufacturer GARMIN: {product_id_val}"
                            )
                    elif product_id_val is not None and manufacturer_enum != Manufacturer.GARMIN:
                        pass

                    time_created = getattr(msg, "time_created", None)

                    fit_data.file_id = FileIdMessageData(
                        file_type=file_type_enum,
                        manufacturer=manufacturer_enum,
                        product=garmin_product_enum if garmin_product_enum else product_id_val,
                        serial_number=getattr(msg, "serial_number", None),
                        time_created=time_created,
                        product_name=getattr(msg, "product_name", None),
                    )

                elif global_id == FileCreatorMessage.ID:
                    msg = actual_message
                    fit_data.creator = FileCreatorMessageData(
                        software_version=getattr(msg, "software_version", None),
                        hardware_version=getattr(msg, "hardware_version", None),
                    )

                elif global_id == LocationSettingsMessage.ID:
                    msg = actual_message
                    location_settings_raw = getattr(msg, "location_settings", None)

                    location_settings_enum = None
                    if location_settings_raw is not None:
                        try:
                            location_settings_enum = LocationSettings(location_settings_raw)
                        except ValueError:
                            self.logger.error(
                                f"Invalid LocationSettings value: {location_settings_raw}. Using None."
                            )

                    fit_data.location_settings = LocationSettingsMessageData(
                        location_settings_enum=location_settings_enum
                    )

                elif global_id == LocationMessage.ID:
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
                            self.logger.error(
                                f"Invalid MapSymbol value {symbol_val} in FIT LocationMessage. Using default."
                            )

                    waypoint = WaypointData(
                        name=getattr(msg, "location_name", None),
                        description=getattr(msg, "description", None),
                        latitude=lat_degrees if lat_degrees is not None else 0.0,
                        longitude=lon_degrees if lon_degrees is not None else 0.0,
                        altitude=getattr(msg, "altitude", None),
                        timestamp=location_datetime_object
                        if location_datetime_object
                        else datetime.now(timezone.utc),
                        symbol=symbol_enum,
                        message_index=getattr(msg, "message_index", None),
                    )
                    parsed_waypoints.append(waypoint)
            except AttributeError as e:
                self.logger.error(
                    f"Attribute error processing message {type(actual_message).__name__} (ID: {global_id}): {e}"
                )
            except Exception as e:
                self.logger.error(
                    f"Unexpected error processing message {type(actual_message).__name__} (ID: {global_id}): {e}"
                )

        fit_data.locations = parsed_waypoints
        return fit_data

    def _build_file_id_message(self, file_id):
        """Build a FileIdMessage from data."""
        fid_msg = FileIdMessage()

        fid_msg.type = file_id.file_type if file_id.file_type is not None else FileType.LOCATIONS
        fid_msg.manufacturer = (
            file_id.manufacturer if file_id.manufacturer is not None else Manufacturer.DEVELOPMENT
        )
        if file_id.product is not None:
            if isinstance(file_id.product, GarminProduct):
                fid_msg.product = file_id.product.value
            else:
                fid_msg.product = file_id.product
        else:
            fid_msg.product = 0 if file_id.manufacturer == Manufacturer.DEVELOPMENT else 1

        fid_msg.serial_number = file_id.serial_number if file_id.serial_number is not None else 0
        fid_msg.time_created = (
            file_id.time_created if file_id.time_created is not None else datetime.now(timezone.utc)
        )
        if file_id.product_name is not None:
            fid_msg.product_name = file_id.product_name

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

    def _build_location_message(self, index, wp_data: WaypointData):
        """Build a LocationMessage from waypoint data."""
        loc_msg = LocationMessage()

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
                loc_msg.symbol = MapSymbol.FLAG_BLUE.value
        else:
            loc_msg.symbol = MapSymbol.FLAG_BLUE.value

        loc_msg.message_index = (
            wp_data.message_index if wp_data.message_index is not None else index
        )

        return loc_msg

    def write_fit_file(
        self, file_path: str, fit_data: LocationsFitFileData
    ) -> Tuple[bool, List[str], List[str]]:
        """Write LocationsFitFileData to a .fit file."""
        errors = []
        builder = FitFileBuilder(auto_define=True, min_string_size=50)

        fid_msg = self._build_file_id_message(fit_data.file_id)
        builder.add(fid_msg)

        creator_msg = self._build_file_creator_message(fit_data.creator)
        builder.add(creator_msg)

        ls_msg = self._build_location_settings_message(fit_data.location_settings)
        builder.add(ls_msg)

        for index, wp_data in enumerate(fit_data.locations):
            loc_msg = self._build_location_message(index, wp_data)
            if loc_msg:
                builder.add(loc_msg)

        if errors:
            for err in errors:
                self.logger.error(f"Critical FIT Write Error: {err}")
            return False, errors

        try:
            fit_file_result = builder.build()
            fit_file_result.to_file(file_path)
            self.logger.log(f"Successfully wrote FIT file to: {file_path}")
            return True, errors

        except Exception as e:
            err_msg = f"Failed to build or write FIT file: {e}"
            self.logger.error(err_msg)
            errors.append(err_msg)
            return False, errors
