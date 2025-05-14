#!/usr/bin/env python
# -*- coding: utf-8 -*-
import platform
import sys

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
