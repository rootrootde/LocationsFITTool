from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, List, Optional

from fit_tool.profile.profile_type import (
    FileType,
    LocationSettings,
    Manufacturer,
    MapSymbol,
)


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
    file_id: FileIdMessageData = field(default_factory=FileIdMessageData)
    creator: FileCreatorMessageData = field(default_factory=FileCreatorMessageData)
    location_settings: Optional[LocationSettingsMessageData] = None
    locations: List[LocationMessageData] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
