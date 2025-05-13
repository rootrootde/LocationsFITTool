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

    return os.path.join(os.path.dirname(_BASE_PATH), "resources", relative_path)
