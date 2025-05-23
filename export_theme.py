from PySide6.QtWidgets import QApplication
from qt_material import export_theme

THEME_DARK = "dark_cyan.xml"
THEME_LIGHT = "light_cyan_500.xml"

extra = {
    # Button colors
    "danger": "#dc3545",
    "warning": "#ffc107",
    "success": "#17a2b8",
    # Font
    # "font_family": "SF Pro",
    "font_size": "13px",
    "line_height": "13px",
    # Density Scale
    "density_scale": "0",
    # Environment hints
    "pyside6": True,
    # 'linux': True,
    "darwin": True,
}

export_theme(
    theme=THEME_DARK,
    qss="theme_dark.qss",
    rcc="resources_theme_dark.qrc",
    output="theme_icons_dark",
    prefix="theme_icons_dark  ",
    invert_secondary=False,
    extra=extra,
)

export_theme(
    theme=THEME_LIGHT,
    qss="theme_light.qss",
    rcc="resources_theme_light.qrc",
    output="theme_icons_light",
    prefix="theme_icons_light  ",
    invert_secondary=True,
    extra=extra,
)
