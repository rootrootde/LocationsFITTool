from dataclasses import asdict, is_dataclass
from datetime import datetime

from location_tool.fit_handler import (
    FileType,
    FitCreatorData,
    FitHeaderData,
    GarminProduct,
    Manufacturer,
)
from PySide6.QtCore import QSettings


# Helper to convert dictionary to FitHeaderData
def _dict_to_fit_header(d):
    if not d or not isinstance(d, dict):
        return None
    try:
        return FitHeaderData(
            file_type=FileType(d["file_type"])
            if d.get("file_type") is not None
            else None,
            manufacturer=Manufacturer(d["manufacturer"])
            if d.get("manufacturer") is not None
            else None,
            product=GarminProduct(d["product"])
            if d.get("product") is not None
            else None,
            serial_number=d.get("serial_number"),
            time_created=datetime.fromisoformat(d["time_created"])
            if d.get("time_created")
            else None,
            product_name=d.get("product_name"),
        )
    except Exception:
        # Log or handle error if conversion fails, e.g. due to enum changes
        return None


# Helper to convert dictionary to FitCreatorData
def _dict_to_fit_creator(d):
    if not d or not isinstance(d, dict):
        return None
    try:
        return FitCreatorData(
            hardware_version=d.get("hardware_version"),
            software_version=d.get("software_version"),
        )
    except Exception:
        return None


def load_fit_header_defaults():
    settings = QSettings("LocationsFITTool", "LocationsFITTool")
    if settings.contains("fit_header_defaults"):
        header_dict = settings.value("fit_header_defaults", None)
        return _dict_to_fit_header(header_dict)
    return None


def load_fit_creator_defaults():
    settings = QSettings("LocationsFITTool", "LocationsFITTool")
    if settings.contains("fit_creator_defaults"):
        creator_dict = settings.value("fit_creator_defaults", None)
        return _dict_to_fit_creator(creator_dict)
    return None


def save_fit_header_defaults(header: FitHeaderData):
    settings = QSettings("LocationsFITTool", "LocationsFITTool")
    if header and is_dataclass(header):
        settings.setValue("fit_header_defaults", asdict(header))
    elif header is None:  # Allow clearing the setting
        settings.remove("fit_header_defaults")


def save_fit_creator_defaults(creator: FitCreatorData):
    settings = QSettings("LocationsFITTool", "LocationsFITTool")
    if creator and is_dataclass(creator):
        settings.setValue("fit_creator_defaults", asdict(creator))
    elif creator is None:  # Allow clearing the setting
        settings.remove("fit_creator_defaults")
