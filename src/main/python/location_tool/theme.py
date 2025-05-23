from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import QFile, QIODevice, QTextStream
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication

from .utils import get_resource_path

THEME_DARK = "dark_cyan.xml"
THEME_LIGHT = "light_cyan_500.xml"


class ThemeManager:
    """Centralized theme management for the application."""

    def __init__(self, appctxt: Any = None):
        """Initialize the theme manager."""
        self.appctxt = appctxt
        self._is_dark_mode = None
        self._current_theme = None
        self._primary_color = None

        # Theme color mapping
        self.THEME_COLORS = {
            "dark_amber.xml": "#ffd740",
            "dark_blue.xml": "#448aff",
            "dark_cyan.xml": "#4dd0e1",
            "dark_lightgreen.xml": "#8bc34a",
            "dark_pink.xml": "#ff4081",
            "dark_purple.xml": "#ab47bc",
            "dark_red.xml": "#ff1744",
            "dark_teal.xml": "#1de9b6",
            "dark_yellow.xml": "#ffff00",
            "light_amber.xml": "#ffc400",
            "light_blue_500.xml": "#03a9f4",
            "light_blue.xml": "#2979ff",
            "light_cyan_500.xml": "#00bcd4",
            "light_cyan.xml": "#00e5ff",
            "light_lightgreen_500.xml": "#8bc34a",
            "light_lightgreen.xml": "#64dd17",
            "light_orange.xml": "#ff3d00",
            "light_pink_500.xml": "#e91e63",
            "light_pink.xml": "#ff4081",
            "light_purple_500.xml": "#9c27b0",
            "light_purple.xml": "#e040fb",
            "light_red_500.xml": "#f44336",
            "light_red.xml": "#ff1744",
            "light_teal_500.xml": "#009688",
            "light_teal.xml": "#1de9b6",
            "light_yellow.xml": "#ffea00",
        }

    @property
    def is_dark_mode(self) -> bool:
        """Detect if system is in dark mode."""
        if self._is_dark_mode is None:
            palette = QApplication.palette()
            window_color = palette.color(QPalette.ColorRole.Window)
            self._is_dark_mode = window_color.lightness() < 128
        return self._is_dark_mode

    @property
    def current_theme_file(self) -> str:
        """Get the appropriate theme file based on system dark mode."""
        return THEME_DARK if self.is_dark_mode else THEME_LIGHT

    @property
    def primary_color(self) -> str:
        """Get the primary color for the current theme."""
        if self._primary_color is None:
            theme_file = self.current_theme_file
            self._primary_color = self.THEME_COLORS.get(theme_file, "#1de9b6")
        return self._primary_color

    def apply_theme(self, app: QApplication) -> None:
        """Apply the appropriate theme to the application."""
        try:
            # Import resources to ensure they're available
            from location_tool.ui import resources_rc

            # Determine QSS file
            qss_filename = "theme_dark.qss" if self.is_dark_mode else "theme_light.qss"

            # Try loading from Qt resources first
            qss_resource_path = f":/{qss_filename}"
            qss_file = QFile(qss_resource_path)

            if qss_file.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text):
                # Load from Qt resources
                stream = QTextStream(qss_file)
                stylesheet_content = stream.readAll()
                qss_file.close()
                print(f"Loaded stylesheet from Qt resources: {qss_filename}")
            else:
                # Fallback to filesystem using get_resource_path
                stylesheet_path = get_resource_path(self.appctxt, qss_filename)
                with open(stylesheet_path, "r") as file:
                    stylesheet_content = file.read()
                print(f"Loaded stylesheet from filesystem: {stylesheet_path}")

            app.setStyleSheet(stylesheet_content)
            print(f"Applied {('dark' if self.is_dark_mode else 'light')} theme")

        except Exception as e:
            print(f"Error applying theme: {e}")
            # Continue with default theme
