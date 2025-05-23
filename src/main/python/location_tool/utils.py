import re
from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QGuiApplication, QIcon, QPainter, QPalette, QPixmap
from PySide6.QtSvg import QSvgRenderer

# This _BASE_PATH will be the directory of utils.py, i.e., .../location_tool/
_BASE_PATH: Path = Path(__file__).resolve().parent

_dark_mode = None
_icon_color = None


def colored_icon(appctxt, svg_path, size: tuple, color=None) -> QIcon:
    """Create a colored QIcon from an SVG file."""
    if color is None:
        palette = QGuiApplication.palette()
        color = palette.color(QPalette.Text)
    abs_path = get_resource_path(appctxt, svg_path)
    renderer = QSvgRenderer(abs_path)
    pixmap = QPixmap(QSize(size[0], size[1]))
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()
    return QIcon(pixmap)


def get_resource_path(appctxt: Optional[Any], relative_path: str) -> str:
    """Get the absolute path to a resource."""
    if appctxt:
        return appctxt.get_resource(relative_path)
    base_dir = _BASE_PATH.parents[1]
    return str(base_dir / "resources" / "base" / relative_path)
