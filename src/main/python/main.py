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
from qt_material import export_theme

if __name__ == "__main__":
    if USE_FBS:
        appctxt = ApplicationContext()
        app = appctxt.app
    else:
        app = QApplication(sys.argv)
        appctxt = None

    try:
        extra = {
            # Button colors
            "danger": "#dc3545",
            "warning": "#ffc107",
            "success": "#17a2b8",
            # Font
            "font_family": "SF Pro",
            "font_size": "13px",
            "line_height": "13px",
            # Density Scale
            "density_scale": "-1",
            # Environment hints
            "pyside6": True,
            # 'linux': True,
            "darwin": True,
        }

        export_theme(
            theme="light_blue_500.xml",
            qss="light_blue_500.qss",
            rcc="resources.rcc",
            output="theme",
            prefix=":/icon/theme/",
            invert_secondary=True,
            extra=extra,
        )

        window = MainWindow(appctxt)
        window.show()
    except Exception as e:
        print(f"Error initializing MainWindow: {e}")
        sys.exit(1)

    exit_code = app.exec()
    sys.exit(exit_code)
