from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, List, Optional

from fit_tool.profile.profile_type import (
    CoursePoint,
    FileType,
    LocationSettings,
    Manufacturer,
    MapSymbol,
    Sport,
    SubSport,
)


@dataclass
class FileIdMessageData:
    file_type: Optional[FileType] = FileType.LOCATIONS
    manufacturer: Optional[Manufacturer] = Manufacturer.DEVELOPMENT
    product: Optional[Any] = 0  # Can be GarminProduct enum or int
    serial_number: Optional[int] = None
    time_created: Optional[datetime] = field(default_factory=lambda: datetime.now(timezone.utc))
    number: int = 0  # File number, used with some file types
    product_name: Optional[str] = None


@dataclass
class FileCreatorMessageData:
    software_version: Optional[int] = 0
    hardware_version: Optional[int] = 0


@dataclass
class LocationSettingsMessageData:
    location_settings_enum: Optional[LocationSettings] = None
    name: Optional[str] = None  # Not standard, but was in original
    message_index: Optional[int] = None  # Not standard for this message


@dataclass
class LocationMessageData:  # Represents a Waypoint in a Locations FIT file
    name: Optional[str] = "Waypoint"
    latitude: float = 0.0
    longitude: float = 0.0
    altitude: Optional[float] = None  # Changed from float to Optional[float] for consistency
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    symbol: Optional[MapSymbol] = (
        MapSymbol.FLAG_BLUE
    )  # Changed to Optional, default to a common one
    message_index: Optional[int] = None
    description: Optional[str] = None


@dataclass
class LocationsFitFileData:
    file_id: FileIdMessageData = field(default_factory=FileIdMessageData)
    creator: Optional[FileCreatorMessageData] = field(
        default_factory=FileCreatorMessageData
    )  # Made Optional
    location_settings: Optional[LocationSettingsMessageData] = None
    locations: List[LocationMessageData] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# Updated dataclasses for Courses (Routes)
@dataclass
class CoursePointMessageData:
    timestamp: Optional[datetime] = None
    position_lat: Optional[float] = None
    position_long: Optional[float] = None
    distance: Optional[float] = None
    type: Optional[CoursePoint] = CoursePoint.GENERIC
    name: Optional[str] = None
    favorite: Optional[bool] = None
    message_index: Optional[int] = None
    # Other relevant fields from CoursePointMesg can be added here


@dataclass
class CourseMessageData:
    name: Optional[str] = None
    sport: Optional[Sport] = Sport.GENERIC
    sub_sport: Optional[SubSport] = SubSport.GENERIC
    capabilities: Optional[int] = None
    message_index: Optional[int] = None  # Added
    points: List[CoursePointMessageData] = field(default_factory=list)  # Added


@dataclass
class CoursesFitFileData:
    file_id: FileIdMessageData = field(default_factory=FileIdMessageData)
    creator: Optional[FileCreatorMessageData] = field(
        default_factory=FileCreatorMessageData
    )  # Made Optional
    courses: List[CourseMessageData] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# New/Updated dataclasses for Activities (Tracks)
@dataclass
class RecordMessageData:
    timestamp: datetime
    position_lat: Optional[float] = None
    position_long: Optional[float] = None
    altitude: Optional[float] = None
    heart_rate: Optional[int] = None
    cadence: Optional[int] = None
    distance: Optional[float] = None
    speed: Optional[float] = None
    power: Optional[int] = None
    grade: Optional[float] = None
    # Other fields can be added as needed, e.g., temperature, etc.


@dataclass
class LapMessageData:
    timestamp: datetime  # Lap end time
    start_time: datetime
    message_index: Optional[int] = None
    total_elapsed_time: Optional[float] = None  # seconds
    total_timer_time: Optional[float] = None  # seconds
    start_position_lat: Optional[float] = None
    start_position_long: Optional[float] = None
    end_position_lat: Optional[float] = None
    end_position_long: Optional[float] = None
    total_distance: Optional[float] = None  # meters
    avg_speed: Optional[float] = None  # m/s
    max_speed: Optional[float] = None  # m/s
    avg_heart_rate: Optional[int] = None  # bpm
    max_heart_rate: Optional[int] = None  # bpm
    avg_cadence: Optional[int] = None  # rpm
    max_cadence: Optional[int] = None  # rpm
    sport: Optional[Sport] = Sport.GENERIC
    # Other relevant fields from LapMesg


@dataclass
class SessionMessageData:
    timestamp: datetime  # Session end time
    start_time: datetime
    message_index: Optional[int] = None
    total_elapsed_time: Optional[float] = None  # seconds
    total_timer_time: Optional[float] = None  # seconds
    total_distance: Optional[float] = None  # meters
    sport: Optional[Sport] = Sport.GENERIC
    sub_sport: Optional[SubSport] = SubSport.GENERIC
    first_lap_index: Optional[int] = 0
    num_laps: Optional[int] = 0
    # Other relevant fields from SessionMesg, e.g. avg_altitude, max_altitude etc.


@dataclass
class ActivityFitFileData:
    file_id: FileIdMessageData = field(default_factory=FileIdMessageData)
    creator: Optional[FileCreatorMessageData] = field(
        default_factory=FileCreatorMessageData
    )  # Made Optional
    sessions: List[SessionMessageData] = field(default_factory=list)
    laps: List[LapMessageData] = field(default_factory=list)
    records: List[RecordMessageData] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
