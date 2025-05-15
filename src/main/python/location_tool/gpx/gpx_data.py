from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

from fit_tool.profile.profile_type import MapSymbol


@dataclass
class GpxWaypointData:
    name: str = "Waypoint"
    latitude: float = 0.0
    longitude: float = 0.0
    altitude: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc))
    symbol: str = MapSymbol.FLAG_BLUE.value
    message_index: int = 0
    description: str = None


@dataclass
class GpxFileData:
    waypoints: List[GpxWaypointData] = field(default_factory=list)
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
