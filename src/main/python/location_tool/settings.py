from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from location_tool.fit_handler import (
    FileType,
    FitCreatorData,
    FitHeaderData,
    GarminProduct,
    Manufacturer,
)
from PySide6.QtCore import QSettings


# Helper to convert dictionary to FitHeaderData
def _dict_to_fit_header(d: Optional[Dict[str, Any]]) -> Optional[FitHeaderData]:
    if not d or not isinstance(d, dict):
        return None
    try:
        # Ensure that enum values are correctly reconstructed if they are stored as their primitive types (e.g., int)
        file_type_val = d.get("file_type")
        manufacturer_val = d.get("manufacturer")
        product_val = d.get("product")
        time_created_val = d.get("time_created")

        return FitHeaderData(
            file_type=FileType(file_type_val) if file_type_val is not None else None,
            manufacturer=Manufacturer(manufacturer_val) if manufacturer_val is not None else None,
            product=GarminProduct(product_val)
            if product_val is not None and isinstance(product_val, int)
            else product_val,  # Handle direct int or already enum
            serial_number=d.get("serial_number"),
            time_created=datetime.fromisoformat(time_created_val) if time_created_val else None,
            product_name=d.get("product_name"),
        )
    except (ValueError, TypeError) as e:  # Catch specific errors for robustness
        # Log or handle error if conversion fails, e.g. due to enum changes or bad data
        print(f"Error converting dict to FitHeaderData: {e}, data: {d}")  # Basic logging
        return None


# Helper to convert dictionary to FitCreatorData
def _dict_to_fit_creator(d: Optional[Dict[str, Any]]) -> Optional[FitCreatorData]:
    if not d or not isinstance(d, dict):
        return None
    try:
        return FitCreatorData(
            hardware_version=d.get("hardware_version"),
            software_version=d.get("software_version"),
        )
    except (ValueError, TypeError) as e:  # Catch specific errors
        print(f"Error converting dict to FitCreatorData: {e}, data: {d}")  # Basic logging
        return None


def load_fit_header_defaults() -> Optional[FitHeaderData]:
    settings: QSettings = QSettings("LocationsFITTool", "LocationsFITTool")
    if settings.contains("fit_header_defaults"):
        header_dict: Optional[Dict[str, Any]] = settings.value("fit_header_defaults", None)
        return _dict_to_fit_header(header_dict)
    return None


def load_fit_creator_defaults() -> Optional[FitCreatorData]:
    settings: QSettings = QSettings("LocationsFITTool", "LocationsFITTool")
    if settings.contains("fit_creator_defaults"):
        creator_dict: Optional[Dict[str, Any]] = settings.value("fit_creator_defaults", None)
        return _dict_to_fit_creator(creator_dict)
    return None


def save_fit_header_defaults(header: Optional[FitHeaderData]) -> None:
    settings: QSettings = QSettings("LocationsFITTool", "LocationsFITTool")
    if header and is_dataclass(header):
        # Ensure datetime is stored in a serializable format (ISO format string)
        header_dict = asdict(header)
        if header_dict.get("time_created") and isinstance(header_dict["time_created"], datetime):
            header_dict["time_created"] = header_dict["time_created"].isoformat()

        # Ensure enums are stored as their values
        if header_dict.get("file_type") and isinstance(header_dict["file_type"], FileType):
            header_dict["file_type"] = header_dict["file_type"].value
        if header_dict.get("manufacturer") and isinstance(
            header_dict["manufacturer"], Manufacturer
        ):
            header_dict["manufacturer"] = header_dict["manufacturer"].value
        if header_dict.get("product") and isinstance(header_dict["product"], GarminProduct):
            header_dict["product"] = header_dict["product"].value

        settings.setValue("fit_header_defaults", header_dict)
    elif header is None:  # Allow clearing the setting
        settings.remove("fit_header_defaults")


def save_fit_creator_defaults(creator: Optional[FitCreatorData]) -> None:
    settings: QSettings = QSettings("LocationsFITTool", "LocationsFITTool")
    if creator and is_dataclass(creator):
        settings.setValue("fit_creator_defaults", asdict(creator))
    elif creator is None:  # Allow clearing the setting
        settings.remove("fit_creator_defaults")
