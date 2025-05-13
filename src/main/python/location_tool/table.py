# filepath: /Users/chris/Coding/LocationsFITTool/src/main/python/location_tool/table.py
import os
from datetime import datetime, timezone

from fit_tool.profile.profile_type import MapSymbol
from location_tool import fit_handler  # For FitLocationData type hint

# Import get_resource_path from main_window.py for now
# This might create a circular import if main_window also imports table.py directly for types.
# Consider moving get_resource_path to a utils.py if it's widely used.
from location_tool.utils import get_resource_path
from PySide6.QtCore import QDateTime, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDateTimeEdit,
    QDoubleSpinBox,
    QHeaderView,
    QStyledItemDelegate,
    QTableWidgetItem,
)


class DateTimeDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QDateTimeEdit(parent)
        editor.setDateTime(QDateTime.currentDateTimeUtc())
        editor.setCalendarPopup(True)
        editor.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        if isinstance(value, QDateTime):
            editor.setDateTime(value)
        elif isinstance(value, datetime):
            editor.setDateTime(
                QDateTime(
                    value.year,
                    value.month,
                    value.day,
                    value.hour,
                    value.minute,
                    value.second,
                    Qt.UTC,
                )
            )
        else:
            try:
                dt_obj = datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(
                    tzinfo=timezone.utc
                )
                editor.setDateTime(
                    QDateTime(
                        dt_obj.year,
                        dt_obj.month,
                        dt_obj.day,
                        dt_obj.hour,
                        dt_obj.minute,
                        dt_obj.second,
                        Qt.UTC,
                    )
                )
            except (ValueError, TypeError):
                editor.setDateTime(QDateTime.currentDateTimeUtc())

    def setModelData(self, editor, model, index):
        dt = editor.dateTime().toPython().replace(tzinfo=timezone.utc)
        model.setData(index, dt.strftime("%Y-%m-%d %H:%M:%S"), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class FloatDelegate(QStyledItemDelegate):
    def __init__(self, decimals=6, parent=None):
        super().__init__(parent)
        self.decimals = decimals

    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setFrame(False)
        editor.setDecimals(self.decimals)
        if index.column() == 1:  # Latitude
            editor.setRange(-90.0, 90.0)
        elif index.column() == 2:  # Longitude
            editor.setRange(-180.0, 180.0)
        elif index.column() == 3:  # Altitude
            editor.setRange(-500.0, 9200.0)
            editor.setDecimals(2)  # Altitude typically has 2 decimals
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        try:
            editor.setValue(float(value))
        except (ValueError, TypeError):
            editor.setValue(0.0)

    def setModelData(self, editor, model, index):
        model.setData(index, f"{editor.value():.{self.decimals}f}", Qt.EditRole)


def setup_waypoints_table(table_widget, parent_widget):
    table_widget.setColumnCount(7)
    headers = [
        "Name",
        "Latitude",
        "Longitude",
        "Altitude",
        "Timestamp",
        "Symbol",
        "Description",
    ]
    table_widget.setHorizontalHeaderLabels(headers)
    table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
    table_widget.setEditTriggers(
        QAbstractItemView.DoubleClicked
        | QAbstractItemView.SelectedClicked
        | QAbstractItemView.EditKeyPressed
    )
    table_widget.setItemDelegateForColumn(
        1, FloatDelegate(decimals=6, parent=parent_widget)
    )  # Latitude
    table_widget.setItemDelegateForColumn(
        2, FloatDelegate(decimals=6, parent=parent_widget)
    )  # Longitude
    table_widget.setItemDelegateForColumn(
        3, FloatDelegate(decimals=2, parent=parent_widget)
    )  # Altitude
    table_widget.setItemDelegateForColumn(
        4, DateTimeDelegate(parent=parent_widget)
    )  # Timestamp

    header = table_widget.horizontalHeader()
    for i in range(table_widget.columnCount()):
        header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
    header.setSectionResizeMode(6, QHeaderView.Stretch)  # Description
    table_widget.horizontalHeader().setStretchLastSection(True)


def populate_waypoints_table(table_widget, waypoints_data: list, appctxt, log_func):
    table_widget.setRowCount(0)
    table_widget.setRowCount(len(waypoints_data))
    for row_idx, wp_data in enumerate(waypoints_data):
        set_table_row_from_wp_data(
            table_widget,
            row_idx,
            wp_data,
            appctxt,
            log_func,
        )
    table_widget.resizeColumnsToContents()


def set_table_row_from_wp_data(
    table_widget,
    row_idx: int,
    wp_data: fit_handler.FitLocationData,
    appctxt,
    log_func,
):
    table_widget.setItem(row_idx, 0, QTableWidgetItem(wp_data.name or ""))
    table_widget.setItem(
        row_idx,
        1,
        QTableWidgetItem(
            f"{wp_data.latitude:.6f}" if wp_data.latitude is not None else "0.000000"
        ),
    )
    table_widget.setItem(
        row_idx,
        2,
        QTableWidgetItem(
            f"{wp_data.longitude:.6f}" if wp_data.longitude is not None else "0.000000"
        ),
    )
    table_widget.setItem(
        row_idx,
        3,
        QTableWidgetItem(
            f"{wp_data.altitude:.2f}" if wp_data.altitude is not None else "0.00"
        ),
    )

    ts_str = (
        wp_data.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        if wp_data.timestamp
        else datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    )
    table_widget.setItem(row_idx, 4, QTableWidgetItem(ts_str))

    symbol_item = QTableWidgetItem()
    symbol_display_text = "N/A"
    symbol_display_tooltip = "N/A"
    icon_path = None

    if wp_data.symbol is not None:
        try:
            symbol_enum = MapSymbol(wp_data.symbol)
            symbol_display_text = f"{symbol_enum.value}"
            symbol_display_tooltip = f"{symbol_enum.name.lower()}"
            icon_file_name = f"{symbol_enum.name.lower()}.png"
            icon_path = os.path.join("icons", icon_file_name)
        except ValueError:
            symbol_display_text = f"{wp_data.symbol} (Unknown)"

    symbol_item.setText(symbol_display_text)
    symbol_item.setToolTip(symbol_display_tooltip)

    if icon_path:
        resolved_icon_path = get_resource_path(appctxt, icon_path)
        icon = QIcon(resolved_icon_path)
        if not icon.isNull():
            symbol_item.setIcon(icon)
        else:
            log_func(
                f"Warning: Icon not found for symbol {symbol_display_text} at {resolved_icon_path}"
            )
    table_widget.setItem(row_idx, 5, symbol_item)
    table_widget.setItem(row_idx, 6, QTableWidgetItem(wp_data.description or ""))
