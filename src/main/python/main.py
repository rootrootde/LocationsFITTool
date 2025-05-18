#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import platform
import sys

# Add the ui_layouts directory to sys.path so import resources_rc works in generated UI files
ui_layouts_path = os.path.join(os.path.dirname(__file__), "location_tool", "ui")
if ui_layouts_path not in sys.path:
    sys.path.insert(0, ui_layouts_path)

try:
    from fbs_runtime.application_context.PySide6 import ApplicationContext

    USE_FBS = True
except ImportError:
    from PySide6.QtWidgets import QApplication

    USE_FBS = False

from location_tool.main_window import MainWindow

FORCE_LIGHT_MODE = False

if __name__ == "__main__":
    if USE_FBS:
        appctxt = ApplicationContext()
        app = appctxt.app
    else:
        app = QApplication(sys.argv)
        appctxt = None

    # Force light mode on macOS
    if FORCE_LIGHT_MODE:
        if platform.system() == "Darwin":
            try:
                from AppKit import NSApp, NSAppearance

                appearance = NSAppearance.appearanceNamed_("NSAppearanceNameAqua")
                NSApp.setAppearance_(appearance)
            except Exception as e:
                print(f"Failed to force light mode: {e}")

    try:
        window = MainWindow(appctxt)
        window.show()
    except Exception as e:
        print(f"Error initializing MainWindow: {e}")
        sys.exit(1)

    exit_code = app.exec()
    sys.exit(exit_code)
