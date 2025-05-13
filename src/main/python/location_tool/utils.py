import os

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
