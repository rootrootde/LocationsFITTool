from datetime import datetime, timezone
from typing import List, Optional, Tuple

import gpxpy.gpx  # For GPXXMLSyntaxException
from fit_tool.profile.profile_type import (
    MapSymbol,
)

from .logger import Logger
from .waypoints import WaypointData


class GpxFileHandler:
    def __init__(self, appctxt):
        """Initialize the GPX file handler."""
        self.appctxt = appctxt
        self.logger = Logger.get_logger()

    def parse_gpx_file(self, file_path: str) -> Tuple[List[WaypointData], List[str]]:
        """Parse a GPX file and return waypoints and errors."""
        waypoints: List[WaypointData] = []
        errors: List[str] = []

        try:
            with open(file_path, "r", encoding="utf-8") as gpx_file_content:
                gpx: gpxpy.gpx.GPX = gpxpy.parse(gpx_file_content)

            # Process top-level waypoints (<wpt>)
            for gpx_wp in gpx.waypoints:
                gpx_timestamp: Optional[datetime] = gpx_wp.time
                if gpx_timestamp:
                    if gpx_timestamp.tzinfo is None:
                        timestamp = gpx_timestamp.replace(tzinfo=timezone.utc)
                    else:
                        timestamp = gpx_timestamp.astimezone(timezone.utc)
                else:
                    timestamp = datetime.now(timezone.utc)

                symbol_to_assign = MapSymbol.AIRPORT
                if gpx_wp.symbol:
                    try:
                        sym_str = gpx_wp.symbol.strip().upper().replace(" ", "_")
                        if sym_str in MapSymbol.__members__:
                            symbol_to_assign = MapSymbol[sym_str]
                        else:
                            try:
                                sym_int = int(gpx_wp.symbol)
                                symbol_to_assign = MapSymbol(sym_int)
                            except ValueError:
                                err_msg = f"GPX waypoint symbol '{gpx_wp.symbol}' is not a recognized MapSymbol name or integer value. Using default."
                                self.logger.error(err_msg)
                                errors.append(err_msg)
                    except Exception as e:
                        err_msg = f"Could not map GPX waypoint symbol '{gpx_wp.symbol}' to FIT symbol: {e}. Using default."
                        self.logger.error(err_msg)
                        errors.append(err_msg)

                altitude = gpx_wp.elevation

                description = gpx_wp.description
                if not description and hasattr(gpx_wp, "comment") and gpx_wp.comment:
                    description = gpx_wp.comment
                elif not description and hasattr(gpx_wp, "cmt") and gpx_wp.cmt:
                    description = gpx_wp.cmt

                name = gpx_wp.name or "Waypoint"

                if gpx_wp.latitude is None or gpx_wp.longitude is None:
                    errors.append(f"Skipping waypoint '{name}' due to missing latitude/longitude.")
                    continue

                wp = WaypointData(
                    name=name,
                    description=description,
                    latitude=gpx_wp.latitude,
                    longitude=gpx_wp.longitude,
                    elevation=altitude,
                    timestamp=timestamp,
                    symbol=symbol_to_assign,
                    message_index=len(waypoints),
                )
                waypoints.append(wp)

            if not waypoints and not errors:
                info_msg = (
                    "GPX file parsed, but no waypoints or route points were found or extracted."
                )
                self.logger.log(info_msg)

        except gpxpy.gpx.GPXXMLSyntaxException as e:
            err_msg = f"Error parsing GPX XML in file '{file_path}': {e}"
            self.logger.error(err_msg)
            errors.append(err_msg)
        except Exception as e:
            err_msg = f"Unexpected error processing GPX file '{file_path}': {e}"
            self.logger.error(err_msg)
            errors.append(err_msg)

        return waypoints, errors

    def write_gpx_file(
        self,
        file_path: str,
        waypoints: List[WaypointData],
    ) -> List[str]:
        """Write waypoints to a GPX file and return errors."""
        errors: List[str] = []

        try:
            gpx = gpxpy.gpx.GPX()

            for i, wp in enumerate(waypoints):
                gpx_wp = gpxpy.gpx.GPXWaypoint(
                    name=wp.name,
                    latitude=wp.latitude,
                    longitude=wp.longitude,
                    elevation=wp.elevation,
                    time=wp.timestamp,
                    symbol=wp.symbol.name.lower()
                    if isinstance(wp.symbol, MapSymbol)
                    else str(wp.symbol).lower(),
                    description=wp.description,
                )
                gpx.waypoints.append(gpx_wp)

            with open(file_path, "w", encoding="utf-8") as gpx_file_content:
                gpx_file_content.write(gpx.to_xml(prettyprint=True))

        except Exception as e:
            err_msg = f"Error saving GPX file '{file_path}': {e}"
            self.logger.error(err_msg)
            errors.append(err_msg)
            return False, errors

        return True, errors
