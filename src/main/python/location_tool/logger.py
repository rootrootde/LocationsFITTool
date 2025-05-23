from datetime import datetime
from typing import Optional

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QTextEdit


class Logger:
    """Logger for application and UI logging."""

    _instance: Optional["Logger"] = None

    def __init__(
        self,
        text_edit_widget: Optional[QTextEdit],
        console_log: bool = True,
        verbose: bool = False,
    ) -> None:
        """Initialize the logger."""
        self.text_edit_widget: Optional[QTextEdit] = text_edit_widget
        self.console_log: bool = console_log

    def _append_message(self, message: str, level: str, color: Optional[str] = None) -> None:
        """Append a formatted message to the log."""
        timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] [{level}] {message}"
        if self.text_edit_widget:
            self.text_edit_widget.append(formatted_message)
            cursor = self.text_edit_widget.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.text_edit_widget.setTextCursor(cursor)
        if self.console_log:
            print(formatted_message)

    def log(self, message: str) -> None:
        """Log an info message."""
        self._append_message(message, "INFO")

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self._append_message(message, "WARNING")

    def error(self, message: str) -> None:
        """Log an error message."""
        self._append_message(message, "ERROR")

    def clear_log(self) -> None:
        """Clear the log display."""
        if self.text_edit_widget:
            self.text_edit_widget.clear()
        self.log("Log cleared.")

    @classmethod
    def get_logger(
        cls, text_edit_widget: Optional[QTextEdit] = None, verbose: bool = False
    ) -> "Logger":
        """Get the singleton logger instance."""
        if cls._instance is None:
            cls._instance = cls(text_edit_widget, verbose=verbose)
        else:
            if text_edit_widget is not None:
                cls._instance.text_edit_widget = text_edit_widget
        return cls._instance
