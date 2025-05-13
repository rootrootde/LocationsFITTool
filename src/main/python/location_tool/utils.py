import os
from datetime import datetime, timezone
from typing import Any, Callable, Optional  # Added Any, Callable

# This _BASE_PATH will be the directory of utils.py, i.e., .../location_tool/
_BASE_PATH: str = os.path.dirname(os.path.abspath(__file__))


def get_resource_path(
    appctxt: Optional[Any], relative_path: str
) -> str:  # appctxt can be fbs.ApplicationContext or None
    """
    Get the absolute path to a resource.
    Works for both normal execution and when packaged by fbs.
    appctxt: The application context from fbs (can be None if not running via fbs).
    relative_path: The path relative to the 'resources' directory
                   (e.g., "icons/my_icon.png").
    """
    if appctxt:
        # Assuming appctxt has a get_resource method that returns a string path
        return appctxt.get_resource(relative_path)

    # For non-fbs execution, the original logic in main_window.py was:
    # os.path.join(BASE_PATH_OF_MAIN_WINDOW, "..", "resources", relative_path)
    # where BASE_PATH_OF_MAIN_WINDOW was .../location_tool.
    # This resolved to .../location_tool/../resources -> .../python/resources.
    # We replicate this, assuming 'resources' is a sibling to the 'location_tool' directory's parent.
    # _BASE_PATH is .../src/main/python/location_tool
    # os.path.dirname(_BASE_PATH) is .../src/main/python
    # So, the resource path becomes .../src/main/python/resources/relative_path
    return os.path.join(os.path.dirname(os.path.dirname(_BASE_PATH)), "resources", relative_path)


def process_raw_timestamp(
    raw_timestamp: Any, logger: Optional[Callable[[str], None]] = None
) -> Optional[datetime]:
    """
    Converts a raw timestamp value to a timezone-aware UTC datetime object.
    The raw_timestamp can be an int/float (assumed seconds since Unix epoch for FIT, not ms)
    or a datetime object.
    FIT timestamps are typically seconds since UTC 00:00 Dec 31 1989.
    datetime.fromtimestamp expects POSIX timestamp (seconds since Jan 1 1970 UTC).
    The fit_tool library handles this conversion when creating datetime objects from FIT timestamps.
    This function primarily ensures timezone awareness if a naive datetime is passed,
    or handles direct int/float if they were somehow not processed by fit_tool.
    """
    if raw_timestamp is None:
        return None

    processed_dt: Optional[datetime] = None
    if isinstance(raw_timestamp, (int, float)):
        try:
            # Assuming raw_timestamp from FIT SDK is seconds from FIT_EPOCH
            # If it's already a POSIX timestamp, this will be wrong.
            # However, fit_tool usually gives datetime objects.
            # This branch is more of a fallback or for non-fit_tool contexts.
            # If it's a direct int from a FIT file (e.g. 'time_created'),
            # it's seconds from FIT_EPOCH.
            # Let's assume if it's int/float here, it's from FIT_EPOCH.
            # If it was fromtimestamp(0), it would be 1970. FIT epoch is later.
            # A common FIT timestamp like 1000000000 is ~2021.
            # datetime.fromtimestamp(raw_timestamp, tz=timezone.utc) would interpret it as POSIX.
            # For now, let's assume fit_tool has already converted it to datetime.
            # If this function receives a raw int/float, it's ambiguous without more context.
            # Given the existing division by 1000, it was likely assumed to be milliseconds
            # from POSIX epoch. Let's stick to that if it's a raw number not from fit_tool.
            # If it *is* from fit_tool and is an int, it's usually already a datetime object.

            # Reverting to previous logic for int/float if not a datetime obj,
            # as fit_tool's process_timestamp usually returns datetime.
            # This branch might be for other uses.
            processed_dt = datetime.fromtimestamp(raw_timestamp / 1000.0, tz=timezone.utc)
            if logger:  # Log if we are actually using this branch, as it's less common for FIT
                logger(f"Processed raw numeric timestamp {raw_timestamp} as ms from POSIX epoch.")

        except Exception as e:
            if logger:
                logger(f"Error converting numeric timestamp ({raw_timestamp}) to datetime: {e}")
    elif isinstance(raw_timestamp, datetime):
        processed_dt = raw_timestamp
        if processed_dt.tzinfo is None:
            processed_dt = processed_dt.replace(tzinfo=timezone.utc)  # Assume UTC if naive
        else:
            processed_dt = processed_dt.astimezone(timezone.utc)  # Convert to UTC
    else:
        if logger:
            logger(f"Unexpected type for timestamp: {type(raw_timestamp)}. Value: {raw_timestamp}")
    return processed_dt
