from main.python.location_tool.utils.utils import logger


class GPXFileHandler:
    def __init__(self, appctxt):
        self.appctxt = appctxt
        self.logger = logger.Logger.get_logger()
