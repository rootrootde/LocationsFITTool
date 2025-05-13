# filepath: /Users/chris/Coding/LocationsFITTool/src/main/python/location_tool/waypoints.py
from datetime import datetime, timezone
from typing import List, Tuple  # Added List and Tuple

from location_tool import fit_handler  # For LocationMessageData type hint


def reindex_waypoints(
    waypoints_data: List[fit_handler.LocationMessageData],
) -> List[fit_handler.LocationMessageData]:
    """Ensure all waypoints have a sequential message_index."""
    for i, wp in enumerate(waypoints_data):  # i is int, wp is LocationMessageData
        wp.message_index = i
    return waypoints_data


def add_waypoint(
    current_waypoints_data: List[fit_handler.LocationMessageData],
) -> Tuple[List[fit_handler.LocationMessageData], fit_handler.LocationMessageData]:
    """Adds a new default waypoint to the list, re-indexes, and returns the updated list and the new waypoint."""
    new_wp_index: int = len(current_waypoints_data)
    new_wp: fit_handler.LocationMessageData = fit_handler.LocationMessageData(
        name=f"Waypoint {new_wp_index}",
        description="",
        latitude=0.0,
        longitude=0.0,
        altitude=0.0,
        timestamp=datetime.now(timezone.utc),
        symbol=0,  # Default symbol, e.g., generic
        message_index=new_wp_index,  # Initial index, will be updated by reindex
    )
    current_waypoints_data.append(new_wp)
    current_waypoints_data = reindex_waypoints(
        current_waypoints_data
    )  # Ensure canonical message_index
    # new_wp object in the list will have its message_index updated by reindex_waypoints
    return current_waypoints_data, new_wp


def delete_waypoints(
    current_waypoints_data: List[fit_handler.LocationMessageData],
    sorted_rows_to_delete: List[int],
) -> Tuple[List[fit_handler.LocationMessageData], int, int]:
    """
    Deletes waypoints from the list based on their row indices.
    Returns the updated list, number of deleted items, and the recommended row index for new selection.
    """
    if not sorted_rows_to_delete:
        return current_waypoints_data, 0, -1

    num_deleted: int = 0
    for row_idx in sorted_rows_to_delete:
        if 0 <= row_idx < len(current_waypoints_data):
            del current_waypoints_data[row_idx]
            num_deleted += 1

    new_selection_row: int = -1
    if current_waypoints_data:  # If list is not empty
        # Try to select the item that was at the top of the deleted block,
        # or the one before it if the last item(s) were deleted.
        new_selection_row = sorted_rows_to_delete[-1]  # Smallest index deleted
        if new_selection_row >= len(current_waypoints_data):
            new_selection_row = len(current_waypoints_data) - 1

    if num_deleted > 0:
        current_waypoints_data = reindex_waypoints(current_waypoints_data)

    return current_waypoints_data, num_deleted, new_selection_row


def delete_all_waypoints() -> List[fit_handler.LocationMessageData]:
    """Returns an empty list, effectively deleting all waypoints."""
    return []
