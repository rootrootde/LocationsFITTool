from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

import gpxpy
import gpxpy.gpx
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel

from .fit_data import (
    ActivityFitFileData,
    CoursesFitFileData,
    LocationsFitFileData,
)
from .tracks import RouteData, RoutePointData, TrackData, TrackPointData, TrackSegmentData
from .waypoints import WaypointData


class GeoDataItem(QStandardItem):
    """Custom item for the GeoDataModel, storing a reference to the underlying data."""

    def __init__(self, text: str = "", data: Optional[Any] = None, is_file_node: bool = False):
        super().__init__(text)
        self._data_object = data
        self._is_file_node = is_file_node
        self.setEditable(False)  # By default, items are not editable

    def data_object(self) -> Optional[Any]:
        return self._data_object

    def set_data_object(self, data: Optional[Any]):
        self._data_object = data

    def is_file_node(self) -> bool:
        return self._is_file_node

    def clone(self) -> "GeoDataItem":
        # QStandardItem.clone() doesn't copy custom attributes, so we override
        cloned_item = GeoDataItem(self.text(), self.data_object(), self.is_file_node())
        cloned_item.setIcon(self.icon())
        return cloned_item


class GeoDataModel(QStandardItemModel):
    """
    A model to store and manage geographical data (waypoints, tracks, routes)
    for display in a QTreeView.
    """

    COLUMN_NAME = 0
    COLUMN_TYPE = 1
    COLUMN_DETAILS = 2
    COLUMN_COUNT = 3  # Total number of columns

    _locations_fit_node: Optional[GeoDataItem] = None

    def __init__(self, parent: Optional[Any] = None):
        super().__init__(parent)
        self.setHorizontalHeaderLabels(["Name", "Type", "Details"])

    def add_file_data(
        self,
        file_name: str,
        file_data: Union[
            LocationsFitFileData, CoursesFitFileData, ActivityFitFileData, gpxpy.gpx.GPX
        ],
        file_path: str,  # Store file path for saving/identification
    ) -> GeoDataItem:
        """
        Adds data from a parsed file (GPX, FIT) to the model.
        file_data can be one of the FitFileData types or a gpxpy.gpx.GPX object.
        Returns the created file node.
        """
        if file_name == "Locations.fit" and isinstance(file_data, LocationsFitFileData):
            file_node = self._get_or_create_locations_fit_node()
            file_node.set_data_object({"file_path": file_path, "file_type": "Locations.fit"})
            file_node.removeRows(0, file_node.rowCount())
        else:
            file_node = GeoDataItem(
                file_name,
                data={"file_path": file_path, "file_type": "Imported File"},
                is_file_node=True,
            )
            file_node.setColumnCount(self.COLUMN_COUNT)
            file_node.setData(file_name, Qt.ItemDataRole.DisplayRole)
            self.invisibleRootItem().appendRow(file_node)

        if isinstance(file_data, LocationsFitFileData):
            file_node.setData("FIT Locations File", Qt.ItemDataRole.ToolTipRole)
            type_item = QStandardItem("FIT Locations")
            details_item = QStandardItem(f"{len(file_data.locations)} waypoints")
            file_node.setChild(self.COLUMN_TYPE, type_item)
            file_node.setChild(self.COLUMN_DETAILS, details_item)

            for loc_msg_data in file_data.locations:
                wp_data = WaypointData(
                    name=loc_msg_data.name or "Waypoint",
                    latitude=loc_msg_data.latitude,
                    longitude=loc_msg_data.longitude,
                    elevation=loc_msg_data.altitude,  # Changed to .elevation as loc_msg_data is WaypointData here
                    timestamp=loc_msg_data.timestamp,
                    symbol=loc_msg_data.symbol,
                    description=loc_msg_data.description,
                )
                self.add_waypoint_to_node(file_node, wp_data)

        elif isinstance(file_data, CoursesFitFileData):
            file_node.setData("FIT Courses File", Qt.ItemDataRole.ToolTipRole)
            type_item = QStandardItem("FIT Courses")
            details_item = QStandardItem(f"{len(file_data.courses)} routes")
            file_node.setChild(self.COLUMN_TYPE, type_item)
            file_node.setChild(self.COLUMN_DETAILS, details_item)

            for course_msg_data in file_data.courses:
                route_points = []
                for cp_msg in course_msg_data.points:
                    route_points.append(
                        RoutePointData(
                            latitude=cp_msg.position_lat,
                            longitude=cp_msg.position_long,
                            timestamp=cp_msg.timestamp,
                            name=cp_msg.name,
                            type=str(cp_msg.type.name) if cp_msg.type else None,
                        )
                    )
                route_data = RouteData(name=course_msg_data.name or "Route", points=route_points)
                self.add_route_to_node(file_node, route_data)

        elif isinstance(file_data, ActivityFitFileData):
            file_node.setData("FIT Activity File", Qt.ItemDataRole.ToolTipRole)
            type_item = QStandardItem("FIT Activity (Track)")
            details_item = QStandardItem("Contains activity data")
            file_node.setChild(self.COLUMN_TYPE, type_item)
            file_node.setChild(self.COLUMN_DETAILS, details_item)

        elif isinstance(file_data, gpxpy.gpx.GPX):
            gpx_content = file_data
            file_node.setData("GPX File", Qt.ItemDataRole.ToolTipRole)
            type_item = QStandardItem("GPX")
            num_wps = len(gpx_content.waypoints)
            num_rts = len(gpx_content.routes)
            num_trks = len(gpx_content.tracks)
            details_str_parts = []
            if num_wps > 0:
                details_str_parts.append(f"{num_wps} wpts")
            if num_rts > 0:
                details_str_parts.append(f"{num_rts} rtes")
            if num_trks > 0:
                details_str_parts.append(f"{num_trks} trks")
            details_item = QStandardItem(
                ", ".join(details_str_parts) if details_str_parts else "Empty"
            )
            file_node.setChild(self.COLUMN_TYPE, type_item)
            file_node.setChild(self.COLUMN_DETAILS, details_item)

            for wp in gpx_content.waypoints:
                wp_data = WaypointData(
                    name=wp.name or "Waypoint",
                    latitude=wp.latitude,
                    longitude=wp.longitude,
                    elevation=wp.elevation,
                    timestamp=(
                        wp.time.replace(tzinfo=timezone.utc)
                        if wp.time and wp.time.tzinfo is None
                        else wp.time
                    )
                    if wp.time
                    else datetime.now(timezone.utc),
                    symbol=None,
                    description=wp.description,
                )
                self.add_waypoint_to_node(file_node, wp_data)

            for route in gpx_content.routes:
                route_points = []
                for pt in route.points:
                    route_points.append(
                        RoutePointData(
                            latitude=pt.latitude,
                            longitude=pt.longitude,
                            elevation=pt.elevation,
                            timestamp=(
                                pt.time.replace(tzinfo=timezone.utc)
                                if pt.time and pt.time.tzinfo is None
                                else pt.time
                            )
                            if pt.time
                            else None,
                            name=pt.name,
                            symbol=pt.symbol,
                            type=pt.type,
                            description=pt.description,
                        )
                    )
                route_data = RouteData(
                    name=route.name or "Route", description=route.description, points=route_points
                )
                self.add_route_to_node(file_node, route_data)

            for track in gpx_content.tracks:
                segments_data = []
                for seg in track.segments:
                    points_data = []
                    for pt_gpx in seg.points:
                        points_data.append(
                            TrackPointData(
                                latitude=pt_gpx.latitude,
                                longitude=pt_gpx.longitude,
                                elevation=pt_gpx.elevation,
                                timestamp=(
                                    pt_gpx.time.replace(tzinfo=timezone.utc)
                                    if pt_gpx.time and pt_gpx.time.tzinfo is None
                                    else pt_gpx.time
                                )
                                if pt_gpx.time
                                else None,
                            )
                        )
                    segments_data.append(TrackSegmentData(points=points_data))
                track_data = TrackData(
                    name=track.name or "Track",
                    description=track.description,
                    segments=segments_data,
                )
                self.add_track_to_node(file_node, track_data)
        return file_node

    def _get_or_create_locations_fit_node(self) -> GeoDataItem:
        """
        Returns the special 'Locations' node for Locations.fit data.
        If it doesn't exist, it's created and added to the model.
        """
        if self._locations_fit_node is None or self._locations_fit_node.model() is None:
            root = self.invisibleRootItem()
            for i in range(root.rowCount()):
                item = root.child(i)
                if isinstance(item, GeoDataItem) and item.text() == "Locations (Device/Default)":
                    self._locations_fit_node = item
                    return item

            self._locations_fit_node = GeoDataItem(
                "Locations (Device/Default)", data={"file_type": "Locations.fit"}, is_file_node=True
            )
            self._locations_fit_node.setColumnCount(self.COLUMN_COUNT)
            self._locations_fit_node.setData(
                "Locations (Device/Default)", Qt.ItemDataRole.DisplayRole
            )
            type_item = QStandardItem("Waypoints")
            details_item = QStandardItem("From device or default")
            self._locations_fit_node.setChild(self.COLUMN_TYPE, type_item)
            self._locations_fit_node.setChild(self.COLUMN_DETAILS, details_item)
            self.invisibleRootItem().appendRow(self._locations_fit_node)
        return self._locations_fit_node

    def add_waypoint_to_node(self, parent_node: GeoDataItem, waypoint: WaypointData):
        """Adds a waypoint as a child of the given parent_node."""
        name = waypoint.name if waypoint.name else "Unnamed Waypoint"
        wp_item = GeoDataItem(name, data=waypoint)
        wp_item.setColumnCount(self.COLUMN_COUNT)
        wp_item.setData(name, Qt.ItemDataRole.DisplayRole)

        type_item = QStandardItem("Waypoint")
        details = f"Lat: {waypoint.latitude:.6f}, Lon: {waypoint.longitude:.6f}"
        if waypoint.elevation is not None:
            details += f", Alt: {waypoint.elevation:.2f}m"
        details_item = QStandardItem(details)

        parent_node.appendRow([wp_item, type_item, details_item])
        if parent_node.is_file_node():
            self._update_file_node_details(parent_node)

    def add_track_to_node(self, parent_node: GeoDataItem, track: TrackData):
        """Adds a track and its segments/points as children of the given parent_node."""
        name = track.name if track.name else "Unnamed Track"
        track_item = GeoDataItem(name, data=track)
        track_item.setColumnCount(self.COLUMN_COUNT)
        track_item.setData(name, Qt.ItemDataRole.DisplayRole)

        type_item = QStandardItem("Track")
        num_segments = len(track.segments)
        num_points = sum(len(seg.points) for seg in track.segments)
        details_item = QStandardItem(f"{num_segments} segments, {num_points} points")

        parent_node.appendRow([track_item, type_item, details_item])

        for i, segment in enumerate(track.segments):
            seg_name = f"Segment {i + 1}"
            seg_item = GeoDataItem(seg_name, data=segment)
            seg_item.setColumnCount(self.COLUMN_COUNT)
            seg_item.setData(seg_name, Qt.ItemDataRole.DisplayRole)

            seg_type_item = QStandardItem("Track Segment")
            seg_details_item = QStandardItem(f"{len(segment.points)} points")
            track_item.appendRow([seg_item, seg_type_item, seg_details_item])

        if parent_node.is_file_node():
            self._update_file_node_details(parent_node)

    def add_route_to_node(self, parent_node: GeoDataItem, route: RouteData):
        """Adds a route and its points as children of the given parent_node."""
        name = route.name if route.name else "Unnamed Route"
        route_item = GeoDataItem(name, data=route)
        route_item.setColumnCount(self.COLUMN_COUNT)
        route_item.setData(name, Qt.ItemDataRole.DisplayRole)

        type_item = QStandardItem("Route")
        details_item = QStandardItem(f"{len(route.points)} points")

        parent_node.appendRow([route_item, type_item, details_item])

        for i, point in enumerate(route.points):
            pt_name = point.name if point.name else f"Route Point {i + 1}"
            pt_item = GeoDataItem(pt_name, data=point)
            pt_item.setColumnCount(self.COLUMN_COUNT)
            pt_item.setData(pt_name, Qt.ItemDataRole.DisplayRole)

            pt_type = QStandardItem("Route Point")
            pt_details = f"Lat: {point.latitude:.6f}, Lon: {point.longitude:.6f}"
            if point.elevation is not None:
                pt_details += f", Alt: {point.elevation:.2f}m"
            pt_details_item = QStandardItem(pt_details)
            route_item.appendRow([pt_item, pt_type, pt_details_item])

        if parent_node.is_file_node():
            self._update_file_node_details(parent_node)

    def _update_file_node_details(self, file_node: GeoDataItem):
        """Updates the 'Details' column of a file node based on its children."""
        if not file_node.is_file_node():
            return

        num_wps, num_rts, num_trks = 0, 0, 0
        for i in range(file_node.rowCount()):
            child_item = file_node.child(i, self.COLUMN_NAME)
            if child_item and isinstance(child_item, GeoDataItem):
                data_obj = child_item.data_object()
                if isinstance(data_obj, WaypointData):
                    num_wps += 1
                elif isinstance(data_obj, RouteData):
                    num_rts += 1
                elif isinstance(data_obj, TrackData):
                    num_trks += 1

        details_str = ""
        if file_node == self._locations_fit_node:
            details_str = f"{num_wps} waypoints"
        else:
            parts = []
            if num_wps > 0:
                parts.append(f"{num_wps} wpts")
            if num_rts > 0:
                parts.append(f"{num_rts} rtes")
            if num_trks > 0:
                parts.append(f"{num_trks} trks")
            details_str = ", ".join(parts) if parts else "Empty"

        details_qitem = file_node.child(self.COLUMN_DETAILS)
        if details_qitem:
            details_qitem.setText(details_str)
        else:
            file_node.setChild(self.COLUMN_DETAILS, QStandardItem(details_str))

    def get_all_data_from_node(self, parent_node: GeoDataItem) -> Dict[str, List[Any]]:
        """
        Retrieves all waypoints, routes, and tracks under a specific file node.
        """
        data = {"waypoints": [], "routes": [], "tracks": []}
        for i in range(parent_node.rowCount()):
            item = parent_node.child(i, self.COLUMN_NAME)
            if item and isinstance(item, GeoDataItem):
                obj = item.data_object()
                if isinstance(obj, WaypointData):
                    data["waypoints"].append(obj)
                elif isinstance(obj, RouteData):
                    data["routes"].append(obj)
                elif isinstance(obj, TrackData):
                    data["tracks"].append(obj)
        return data

    def get_all_waypoints_from_locations_node(self) -> List[WaypointData]:
        """Retrieves all waypoints specifically from the 'Locations (Device/Default)' node."""
        locations_node = self._get_or_create_locations_fit_node()
        waypoints = []
        for i in range(locations_node.rowCount()):
            item = locations_node.child(i, self.COLUMN_NAME)
            if item and isinstance(item, GeoDataItem):
                obj = item.data_object()
                if isinstance(obj, WaypointData):
                    waypoints.append(obj)
        return waypoints

    def clear_data(self):
        """Clears all data from the model."""
        if self._locations_fit_node and self._locations_fit_node.model() is not None:
            self._locations_fit_node.removeRows(0, self._locations_fit_node.rowCount())
            self._update_file_node_details(self._locations_fit_node)

        root = self.invisibleRootItem()
        rows_to_remove = []
        for i in range(root.rowCount()):
            if root.child(i) != self._locations_fit_node:
                rows_to_remove.append(i)

        for i in sorted(rows_to_remove, reverse=True):
            root.removeRow(i)

        if not (self._locations_fit_node and self._locations_fit_node.model() is not None):
            self._locations_fit_node = None
            self._get_or_create_locations_fit_node()

        if self.columnCount() == 0 and self.rowCount() == 0:
            self.setHorizontalHeaderLabels(["Name", "Type", "Details"])

    def remove_selected_items(self, selected_indexes: List[QModelIndex]):
        """Removes selected items from the model."""
        parent_map: Dict[QModelIndex, List[int]] = {}
        top_level_rows_to_remove = []

        items_to_process = set()
        for index in selected_indexes:
            if index.isValid():
                items_to_process.add(self.itemFromIndex(index.siblingAtColumn(0)))

        actual_items_to_remove = []
        for item in items_to_process:
            if not item:
                continue

            if item == self._locations_fit_node and item.parent() is self.invisibleRootItem():
                self._locations_fit_node.removeRows(0, self._locations_fit_node.rowCount())
                self._update_file_node_details(self._locations_fit_node)
                continue

            actual_items_to_remove.append(item)

        for item in actual_items_to_remove:
            parent_item = item.parent()
            if parent_item is self.invisibleRootItem() or parent_item is None:
                top_level_rows_to_remove.append(item.row())
            else:
                parent_index = parent_item.index()
                if parent_index not in parent_map:
                    parent_map[parent_index] = []
                parent_map[parent_index].append(item.row())

        for parent_idx, rows in parent_map.items():
            parent_item_for_children = self.itemFromIndex(parent_idx)
            if parent_item_for_children:
                for row in sorted(list(set(rows)), reverse=True):
                    parent_item_for_children.removeRow(row)
                if (
                    isinstance(parent_item_for_children, GeoDataItem)
                    and parent_item_for_children.is_file_node()
                ):
                    self._update_file_node_details(parent_item_for_children)

        root_item = self.invisibleRootItem()
        for row in sorted(list(set(top_level_rows_to_remove)), reverse=True):
            item_to_remove = root_item.child(row)
            if item_to_remove == self._locations_fit_node:
                self._locations_fit_node.removeRows(0, self._locations_fit_node.rowCount())
                self._update_file_node_details(self._locations_fit_node)
            else:
                root_item.removeRow(row)
