#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

try:
    from fbs_runtime.application_context.PySide6 import ApplicationContext

    USE_FBS = True
except ImportError:
    from PySide6.QtWidgets import QApplication

    USE_FBS = False

from location_tool.gui import MainWindow

if __name__ == "__main__":
    if USE_FBS:
        appctxt = ApplicationContext()
        app = appctxt.app
    else:
        app = QApplication(sys.argv)
        appctxt = None  # Or some dummy object if MainWindow expects it

    try:
        window = MainWindow(appctxt)
        window.show()
    except Exception as e:
        print(f"Error initializing MainWindow: {e}")
        sys.exit(1)

    exit_code = app.exec()
    sys.exit(exit_code)
