#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from fbs_runtime.application_context.PySide6 import ApplicationContext
from location_tool.gui import MainWindow

if __name__ == "__main__":
    appctxt = ApplicationContext()
    try:
        window = MainWindow(appctxt)
        window.show()

    except Exception as e:
        print(f"Error initializing MainWindow: {e}")
        sys.exit(1)
    exit_code = appctxt.app.exec()
    sys.exit(exit_code)
