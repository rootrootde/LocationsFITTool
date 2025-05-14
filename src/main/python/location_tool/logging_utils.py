from datetime import datetime
from typing import Optional

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QTextEdit


class Logger:
    _instance: Optional["Logger"] = None

    def __init__(
        self,
        text_edit_widget: Optional[QTextEdit],
        app_name: str = "Application",
        console_log: bool = True,
    ) -> None:
        self.text_edit_widget: Optional[QTextEdit] = text_edit_widget
        self.app_name: str = app_name
        self.console_log: bool = console_log

    def _format_message(self, message: str, level: str = "INFO") -> str:
        timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] [{self.app_name}] [{level}] {message}"

    def log(self, message: str) -> None:
        formatted_message: str = self._format_message(message, "INFO")
        if self.text_edit_widget:
            self.text_edit_widget.appendPlainText(formatted_message)
            # Auto-scroll to the bottom
            scrollbar = self.text_edit_widget.verticalScrollBar()
            if scrollbar:  # Check if scrollbar exists
                scrollbar.setValue(scrollbar.maximum())
        if self.console_log:
            print(formatted_message)

    def error(self, message: str) -> None:
        formatted_message: str = self._format_message(message, "ERROR")
        if self.text_edit_widget:
            self.text_edit_widget.appendPlainText(formatted_message)
            # Auto-scroll to the bottom
            cursor: QTextCursor = self.text_edit_widget.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.text_edit_widget.setTextCursor(cursor)

        if self.console_log:
            print(
                formatted_message
            )  # Consider printing errors to stderr: import sys; print(formatted_message, file=sys.stderr)

    def warning(self, message: str) -> None:
        formatted_message: str = self._format_message(message, "WARNING")
        if self.text_edit_widget:
            self.text_edit_widget.appendPlainText(formatted_message)
            # Auto-scroll to the bottom
            cursor: QTextCursor = self.text_edit_widget.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.text_edit_widget.setTextCursor(cursor)
        if self.console_log:
            print(formatted_message)

    def clear_log(self) -> None:
        if self.text_edit_widget:
            self.text_edit_widget.clear()
        self.log("Log cleared.")

    @classmethod
    def init(cls, text_edit_widget: Optional[QTextEdit], app_name: str = "Application") -> "Logger":
        if cls._instance is None:
            cls._instance = cls(text_edit_widget, app_name=app_name)
        return cls._instance

    @classmethod
    def get(cls) -> "Logger":
        if cls._instance is None:
            raise RuntimeError("Logger not initialized. Call Logger.init() first.")
        return cls._instance
