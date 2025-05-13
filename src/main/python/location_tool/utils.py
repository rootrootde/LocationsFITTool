import os
from datetime import datetime, timezone
from typing import Optional

# This _BASE_PATH will be the directory of utils.py, i.e., .../location_tool/
_BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def get_resource_path(appctxt, relative_path):
    """
    Get the absolute path to a resource.
    Works for both normal execution and when packaged by fbs.
    appctxt: The application context from fbs (can be None if not running via fbs).
    relative_path: The path relative to the 'resources' directory
                   (e.g., "icons/my_icon.png").
    """
    if appctxt:
        return appctxt.get_resource(relative_path)

    # For non-fbs execution, the original logic in main_window.py was:
    # os.path.join(BASE_PATH_OF_MAIN_WINDOW, "..", "resources", relative_path)
    # where BASE_PATH_OF_MAIN_WINDOW was .../location_tool.
    # This resolved to .../location_tool/../resources -> .../python/resources.
    # We replicate this, assuming 'resources' is a sibling to the 'location_tool' directory's parent.
    # _BASE_PATH is .../src/main/python/location_tool
    # os.path.dirname(_BASE_PATH) is .../src/main/python
    # So, the resource path becomes .../src/main/python/resources/relative_path
    return os.path.join(os.path.dirname(_BASE_PATH), "resources", relative_path)


def process_raw_timestamp(raw_timestamp: any, logger=None) -> Optional[datetime]:
    """
    Converts a raw timestamp value to a timezone-aware UTC datetime object.
    The raw_timestamp can be an int/float (assumed ms since Unix epoch)
    or a datetime object.
    """
    if raw_timestamp is None:
        return None

    processed_dt = None
    if isinstance(raw_timestamp, (int, float)):
        try:
            processed_dt = datetime.fromtimestamp(
                raw_timestamp / 1000.0, tz=timezone.utc
            )
        except Exception as e:
            if logger:
                logger(f"Error converting timestamp ({raw_timestamp}) to datetime: {e}")
    elif isinstance(raw_timestamp, datetime):
        processed_dt = raw_timestamp
        if processed_dt.tzinfo is None:
            processed_dt = processed_dt.replace(tzinfo=timezone.utc)
        else:
            processed_dt = processed_dt.astimezone(timezone.utc)
    else:
        if logger:
            logger(
                f"Unexpected type for timestamp: {type(raw_timestamp)}. Value: {raw_timestamp}"
            )
    return processed_dt
