from PySide6.QtWidgets import QApplication
from qt_material import export_theme

extra = {
    # Button colors
    "danger": "#dc3545",
    "warning": "#ffc107",
    "success": "#17a2b8",
    # Font
    # "font_family": "Roboto",
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
    theme="dark_teal.xml",
    qss="theme.qss",
    rcc="resources_theme.qrc",
    output="theme_icons",
    prefix="theme_icons  ",
    invert_secondary=False,
    extra=extra,
)
