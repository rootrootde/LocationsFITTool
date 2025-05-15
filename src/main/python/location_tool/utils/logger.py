from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QTextEdit


class Logger:
    _instance: Optional["Logger"] = None

    def __init__(
        self,
        text_edit_widget: Optional[QTextEdit],
        console_log: bool = True,
        verbose: bool = False,
    ) -> None:
        self.text_edit_widget: Optional[QTextEdit] = text_edit_widget
        self.console_log: bool = console_log
        self.verbose: bool = verbose

    def _format_message(self, message: str, level: str = "INFO") -> str:
        timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        location: str = ""

        if self.verbose:
            import inspect

            frame = inspect.currentframe()
            outer_frames = inspect.getouterframes(frame)
            if len(outer_frames) >= 3:
                caller_frame = outer_frames[2]
                filename = str(Path(caller_frame.filename).name)
                lineno = caller_frame.lineno
                funcname = caller_frame.function
                location = f" [{filename}:{funcname}:{lineno}]"

        return f"[{timestamp}] [{level}]{location} {message}"

    def log(self, message: str) -> None:
        formatted_message: str = self._format_message(message, "INFO")
        if self.text_edit_widget:
            self.text_edit_widget.append(formatted_message)
            # Auto-scroll to the bottom
            scrollbar = self.text_edit_widget.verticalScrollBar()
            if scrollbar:  # Check if scrollbar exists
                scrollbar.setValue(scrollbar.maximum())
        if self.console_log:
            print(formatted_message)

    def error(self, message: str) -> None:
        formatted_message: str = self._format_message(message, "ERROR")
        if self.text_edit_widget:
            self.text_edit_widget.append(formatted_message)
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
            self.text_edit_widget.append(formatted_message)
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
    def get_logger(
        cls, text_edit_widget: Optional[QTextEdit] = None, verbose: bool = False
    ) -> "Logger":
        if cls._instance is None:
            cls._instance = cls(text_edit_widget, verbose=verbose)
        else:
            # Always update the widget if a new one is provided
            if text_edit_widget is not None:
                cls._instance.text_edit_widget = text_edit_widget
        return cls._instance
