# filepath: /Users/chris/Coding/LocationsFITTool/src/main/python/location_tool/logging_utils.py
from datetime import datetime

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QTextEdit


class Logger:
    def __init__(
        self,
        text_edit_widget: QTextEdit,
        app_name: str = "Application",
        console_log: bool = True,
    ):
        self.text_edit_widget = text_edit_widget
        self.app_name = app_name
        self.console_log = console_log

    def _format_message(self, message: str, level: str = "INFO") -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] [{self.app_name}] [{level}] {message}"

    def log(self, message: str):
        formatted_message = self._format_message(message, "INFO")
        if self.text_edit_widget:
            self.text_edit_widget.appendPlainText(formatted_message)
            # Auto-scroll to the bottom
            scrollbar = self.text_edit_widget.verticalScrollBar()
            if scrollbar:  # Check if scrollbar exists
                scrollbar.setValue(scrollbar.maximum())
        if self.console_log:
            print(formatted_message)

    def error(self, message: str):
        formatted_message = self._format_message(message, "ERROR")
        if self.text_edit_widget:
            self.text_edit_widget.appendPlainText(formatted_message)
            # Auto-scroll to the bottom
            cursor = self.text_edit_widget.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.text_edit_widget.setTextCursor(cursor)

        if self.console_log:
            print(
                formatted_message
            )  # Consider printing errors to stderr: import sys; print(formatted_message, file=sys.stderr)

    def warning(self, message: str):
        formatted_message = self._format_message(message, "WARNING")
        if self.text_edit_widget:
            self.text_edit_widget.appendPlainText(formatted_message)
            # Auto-scroll to the bottom
            cursor = self.text_edit_widget.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.text_edit_widget.setTextCursor(cursor)
        if self.console_log:
            print(formatted_message)

    def clear_log(self):
        if self.text_edit_widget:
            self.text_edit_widget.clear()
        self.log("Log cleared.")
