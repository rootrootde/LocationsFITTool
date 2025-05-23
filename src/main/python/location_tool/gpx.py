from datetime import datetime, timezone
from typing import List, Optional, Tuple

import gpxpy.gpx  # For GPXXMLSyntaxException
from fit_tool.profile.profile_type import (
    MapSymbol,
)

from .logger import Logger
from .tracks import (
    RouteData,
    RoutePointData,
    TrackData,
    TrackPointData,
    TrackSegmentData,
)
from .waypoints import WaypointData


class GpxFileHandler:
    def __init__(self, appctxt):
        """Initialize the GPX file handler."""
        self.appctxt = appctxt
        self.logger = Logger.get_logger()

    def parse_gpx_file(
        self, file_path: str
    ) -> Tuple[List[WaypointData], List[TrackData], List[RouteData], List[str]]:
        """Parse a GPX file and return waypoints, tracks, routes, and errors."""
        waypoints: List[WaypointData] = []
        tracks: List[TrackData] = []
        routes: List[RouteData] = []
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

            # Process tracks (<trk>)
            for gpx_track in gpx.tracks:
                track_segments: List[TrackSegmentData] = []
                for gpx_segment in gpx_track.segments:
                    segment_points: List[TrackPointData] = []
                    for gpx_point in gpx_segment.points:
                        if gpx_point.latitude is None or gpx_point.longitude is None:
                            errors.append(
                                f"Skipping track point in track '{gpx_track.name or 'Unnamed Track'}' due to missing latitude/longitude."
                            )
                            continue

                        point_timestamp: Optional[datetime] = gpx_point.time
                        if point_timestamp:
                            if point_timestamp.tzinfo is None:
                                timestamp = point_timestamp.replace(tzinfo=timezone.utc)
                            else:
                                timestamp = point_timestamp.astimezone(timezone.utc)
                        else:
                            timestamp = (
                                None  # Or datetime.now(timezone.utc) if a default is preferred
                            )

                        tp = TrackPointData(
                            latitude=gpx_point.latitude,
                            longitude=gpx_point.longitude,
                            elevation=gpx_point.elevation,
                            timestamp=timestamp,
                        )
                        segment_points.append(tp)
                    if segment_points:
                        track_segments.append(TrackSegmentData(points=segment_points))

                if track_segments:
                    track = TrackData(
                        name=gpx_track.name,
                        description=gpx_track.description,
                        segments=track_segments,
                    )
                    tracks.append(track)

            # Process routes (<rte>)
            for gpx_route in gpx.routes:
                route_points: List[RoutePointData] = []
                for gpx_route_point in gpx_route.points:
                    if gpx_route_point.latitude is None or gpx_route_point.longitude is None:
                        errors.append(
                            f"Skipping route point in route '{gpx_route.name or 'Unnamed Route'}' due to missing latitude/longitude."
                        )
                        continue

                    rp_timestamp: Optional[datetime] = gpx_route_point.time
                    if rp_timestamp:
                        if rp_timestamp.tzinfo is None:
                            timestamp = rp_timestamp.replace(tzinfo=timezone.utc)
                        else:
                            timestamp = rp_timestamp.astimezone(timezone.utc)
                    else:
                        timestamp = None  # Or datetime.now(timezone.utc) if a default is preferred

                    rp_description = gpx_route_point.description
                    if (
                        not rp_description
                        and hasattr(gpx_route_point, "comment")
                        and gpx_route_point.comment
                    ):
                        rp_description = gpx_route_point.comment
                    elif (
                        not rp_description
                        and hasattr(gpx_route_point, "cmt")
                        and gpx_route_point.cmt
                    ):
                        rp_description = gpx_route_point.cmt

                    rp = RoutePointData(
                        latitude=gpx_route_point.latitude,
                        longitude=gpx_route_point.longitude,
                        elevation=gpx_route_point.elevation,
                        timestamp=timestamp,
                        name=gpx_route_point.name,
                        symbol=gpx_route_point.symbol,
                        type=gpx_route_point.type,
                        description=rp_description,
                    )
                    route_points.append(rp)

                if route_points:
                    route = RouteData(
                        name=gpx_route.name,
                        description=gpx_route.description,
                        points=route_points,
                    )
                    routes.append(route)

            if not waypoints and not tracks and not routes and not errors:
                info_msg = (
                    "GPX file parsed, but no waypoints, tracks, or routes were found or extracted."
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

        return waypoints, tracks, routes, errors

    def write_gpx_file(
        self,
        file_path: str,
        waypoints: List[WaypointData],
        tracks: List[TrackData],
        routes: List[RouteData],
    ) -> Tuple[bool, List[str]]:
        """Write waypoints, tracks, and routes to a GPX file and return errors."""
        errors: List[str] = []
        gpx = gpxpy.gpx.GPX()

        # Write Waypoints
        for wp in waypoints:
            gpx_wp = gpxpy.gpx.GPXWaypoint()
            gpx_wp.name = wp.name
            gpx_wp.latitude = wp.latitude
            gpx_wp.longitude = wp.longitude
            gpx_wp.elevation = wp.elevation
            gpx_wp.time = wp.timestamp
            if wp.symbol:
                gpx_wp.symbol = (
                    wp.symbol.name.lower()
                    if isinstance(wp.symbol, MapSymbol)
                    else str(wp.symbol).lower()
                )
            gpx_wp.description = wp.description
            # Add other WaypointData fields if gpxpy supports them (e.g., comment, type)
            gpx.waypoints.append(gpx_wp)

        # Write Tracks
        for track_data in tracks:
            gpx_track = gpxpy.gpx.GPXTrack()
            gpx_track.name = track_data.name
            gpx_track.description = track_data.description
            # gpx_track.number = track_data.number # If you add number to TrackData
            for segment_data in track_data.segments:
                gpx_segment = gpxpy.gpx.GPXTrackSegment()
                for point_data in segment_data.points:
                    gpx_point = gpxpy.gpx.GPXTrackPoint()
                    gpx_point.latitude = point_data.latitude
                    gpx_point.longitude = point_data.longitude
                    gpx_point.elevation = point_data.elevation
                    gpx_point.time = point_data.timestamp
                    # Add other TrackPointData fields if gpxpy supports them
                    gpx_segment.points.append(gpx_point)
                if gpx_segment.points:
                    gpx_track.segments.append(gpx_segment)
            if gpx_track.segments:
                gpx.tracks.append(gpx_track)

        # Write Routes
        for route_data in routes:
            gpx_route = gpxpy.gpx.GPXRoute()
            gpx_route.name = route_data.name
            gpx_route.description = route_data.description
            # gpx_route.number = route_data.number # If you add number to RouteData
            for point_data in route_data.points:
                gpx_route_point = gpxpy.gpx.GPXRoutePoint()
                gpx_route_point.latitude = point_data.latitude
                gpx_route_point.longitude = point_data.longitude
                gpx_route_point.elevation = point_data.elevation
                gpx_route_point.time = point_data.timestamp
                gpx_route_point.name = point_data.name
                gpx_route_point.symbol = point_data.symbol
                gpx_route_point.type = point_data.type
                gpx_route_point.comment = (
                    point_data.description
                )  # GPX uses 'cmt' for route point descriptions
                # Add other RoutePointData fields if gpxpy supports them
                gpx_route.points.append(gpx_route_point)
            if gpx_route.points:
                gpx.routes.append(gpx_route)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(gpx.to_xml())
            return True, errors
        except Exception as e:
            err_msg = f"Error writing GPX file '{file_path}': {e}"
            self.logger.error(err_msg)
            errors.append(err_msg)
            return False, errors
