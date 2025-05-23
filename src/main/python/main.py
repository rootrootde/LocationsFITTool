#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

try:
    from fbs_runtime.application_context.PySide6 import ApplicationContext

    USE_FBS = True
except ImportError:
    from PySide6.QtWidgets import QApplication

    USE_FBS = False

from location_tool.main_window import MainWindow
from location_tool.theme import ThemeManager

if __name__ == "__main__":
    if USE_FBS:
        appctxt = ApplicationContext()
        app = appctxt.app
    else:
        app = QApplication(sys.argv)
        appctxt = None

    try:
        # Create theme manager and apply theme
        theme_manager = ThemeManager(appctxt)
        theme_manager.apply_theme(app)

        # Create main window with theme manager
        window = MainWindow(appctxt, theme_manager)
        window.show()

    except Exception as e:
        print(f"Error initializing application: {e}")
        sys.exit(1)

    exit_code = app.exec()
    sys.exit(exit_code)
