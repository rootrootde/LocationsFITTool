from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class TrackPointData:
    latitude: float
    longitude: float
    elevation: Optional[float] = None
    timestamp: Optional[datetime] = None


@dataclass
class TrackSegmentData:
    points: List[TrackPointData] = field(default_factory=list)


@dataclass
class TrackData:
    name: Optional[str] = None
    description: Optional[str] = None
    segments: List["TrackSegmentData"] = field(default_factory=list)


@dataclass
class RoutePointData:
    latitude: float
    longitude: float
    elevation: Optional[float] = None
    timestamp: Optional[datetime] = None
    name: Optional[str] = None
    symbol: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None


@dataclass
class RouteData:
    name: Optional[str] = None
    description: Optional[str] = None
    points: List[RoutePointData] = field(default_factory=list)
