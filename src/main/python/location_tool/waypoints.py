from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional

from fit_tool.profile.profile_type import MapSymbol
from PySide6.QtCore import QDateTime, QEvent, QModelIndex, QSize, Qt, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDateTimeEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QGridLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from . import logger
from .utils import get_resource_path


@dataclass
class WaypointData:
    name: Optional[str] = "Waypoint"
    latitude: float = 0.0  # Degrees
    longitude: float = 0.0  # Degrees
    altitude: Optional[float] = None  # Meters
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    symbol: MapSymbol = MapSymbol.AIRPORT
    message_index: Optional[int] = None
    description: Optional[str] = None


class TableColumn(Enum):
    NAME = 0
    LATITUDE = 1
    LONGITUDE = 2
    ALTITUDE = 3
    TIMESTAMP = 4
    SYMBOL = 5
    DESCRIPTION = 6


class DateTimeDelegate(QStyledItemDelegate):
    def createEditor(
        self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex
    ) -> QDateTimeEdit:
        editor = QDateTimeEdit(parent)
        editor.setDateTime(QDateTime.currentDateTimeUtc())
        editor.setCalendarPopup(True)
        editor.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        return editor

    def setEditorData(self, editor: QDateTimeEdit, index: QModelIndex) -> None:
        value: Any = index.model().data(index, Qt.EditRole)
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
                dt_obj: datetime = datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(
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

    def setModelData(self, editor: QDateTimeEdit, model: Any, index: QModelIndex) -> None:
        dt: datetime = editor.dateTime().toPython().replace(tzinfo=timezone.utc)
        model.setData(index, dt.strftime("%Y-%m-%d %H:%M:%S"), Qt.EditRole)

    def updateEditorGeometry(
        self, editor: QDateTimeEdit, option: QStyleOptionViewItem, index: QModelIndex
    ) -> None:
        editor.setGeometry(option.rect)


class FloatDelegate(QStyledItemDelegate):
    def __init__(self, decimals: int = 6, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.decimals: int = decimals

    def createEditor(
        self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex
    ) -> QDoubleSpinBox:
        editor = QDoubleSpinBox(parent)
        editor.setFrame(False)
        if index.column() == 1:  # Latitude
            editor.setDecimals(self.decimals)
            editor.setRange(-90.0, 90.0)
        elif index.column() == 2:  # Longitude
            editor.setDecimals(self.decimals)
            editor.setRange(-180.0, 180.0)
        elif index.column() == 3:  # Altitude
            editor.setDecimals(0)  # Altitude as int, no decimals
            editor.setRange(-500, 9200)
        return editor

    def setEditorData(self, editor: QDoubleSpinBox, index: QModelIndex) -> None:
        value: Any = index.model().data(index, Qt.EditRole)
        try:
            if index.column() == 3:  # Altitude
                editor.setValue(int(float(value)))
            else:
                editor.setValue(float(value))
        except (ValueError, TypeError):
            editor.setValue(0.0)

    def setModelData(self, editor: QDoubleSpinBox, model: Any, index: QModelIndex) -> None:
        if index.column() == 3:  # Altitude
            model.setData(index, str(int(editor.value())), Qt.EditRole)
        else:
            model.setData(index, f"{editor.value():.{self.decimals}f}", Qt.EditRole)


class AltitudeDelegate(QStyledItemDelegate):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

    def createEditor(
        self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex
    ) -> QDoubleSpinBox:
        editor = QDoubleSpinBox(parent)
        editor.setDecimals(0)
        editor.setRange(-500, 9200)
        editor.setFrame(False)
        return editor

    def setEditorData(self, editor: QDoubleSpinBox, index: QModelIndex) -> None:
        value: Any = index.model().data(index, Qt.EditRole)
        try:
            editor.setValue(int(float(value)))
        except (ValueError, TypeError):
            editor.setValue(0)

    def setModelData(self, editor: QDoubleSpinBox, model: Any, index: QModelIndex) -> None:
        model.setData(index, str(int(editor.value())), Qt.EditRole)


class DescriptionDialog(QDialog):
    def __init__(self, parent: Optional[QWidget] = None, initial_text: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Edit Description")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlainText(initial_text)
        layout.addWidget(self.text_edit)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_text(self) -> str:
        return self.text_edit.toPlainText()


class DescriptionDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        # Prevent inline editor
        return None

    def editorEvent(self, event, model, option, index):
        # Only handle double-click events
        if event.type() == QEvent.MouseButtonDblClick:
            current_text = index.model().data(index, Qt.EditRole)
            dialog = DescriptionDialog(option.widget, initial_text=current_text or "")
            if dialog.exec() == QDialog.Accepted:
                new_text = dialog.get_text()
                model.setData(index, new_text, Qt.EditRole)
            return True  # Event handled
        return super().editorEvent(event, model, option, index)

    def setEditorData(self, editor, index):
        pass  # Not used

    def setModelData(self, editor, model, index):
        pass  # Not used


class SymbolPickerDialog(QDialog):
    def __init__(
        self, parent: Optional[QWidget], appctxt: Any, current_symbol: Optional[MapSymbol] = None
    ):
        super().__init__(parent)
        self.setWindowTitle("Select Symbol")
        self.setMinimumWidth(700)
        self.selected_symbol = None
        self.appctxt = appctxt
        self.symbols = list(MapSymbol)
        grid_layout = QVBoxLayout(self)
        grid = QGridLayout()
        icon_size = 32
        col_count = 17
        for idx, symbol in enumerate(self.symbols):
            row = idx // col_count
            col = idx % col_count
            icon_file_name = f"{symbol.name.lower()}.png"
            icon_path = str(Path("wpt_icons") / icon_file_name)
            resolved_icon_path = get_resource_path(self.appctxt, icon_path)
            btn = QPushButton()
            btn.setIcon(QIcon(resolved_icon_path))
            btn.setIconSize(QSize(icon_size, icon_size))
            btn.setToolTip(symbol.name)
            btn.setFixedSize(icon_size + 12, icon_size + 12)
            btn.clicked.connect(lambda checked, s=symbol: self._select_symbol(s))
            grid.addWidget(btn, row, col)
            if current_symbol == symbol:
                btn.setStyleSheet("border: 2px solid blue;")
        grid_layout.addLayout(grid)
        button_box = QDialogButtonBox(QDialogButtonBox.Cancel)
        button_box.rejected.connect(self.reject)
        grid_layout.addWidget(button_box)

    def _select_symbol(self, symbol):
        self.selected_symbol = symbol
        self.accept()

    def get_selected_symbol(self):
        return self.selected_symbol


class SymbolDelegate(QStyledItemDelegate):
    def __init__(self, appctxt: Any, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.appctxt = appctxt

    def createEditor(self, parent, option, index):
        # Prevent inline editor
        return None

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonDblClick:
            current_value = index.model().data(index, Qt.EditRole)
            try:
                current_symbol = MapSymbol(int(current_value))
            except Exception:
                current_symbol = None
            dialog = SymbolPickerDialog(option.widget, self.appctxt, current_symbol)
            if dialog.exec() == QDialog.Accepted:
                symbol = dialog.get_selected_symbol()
                if symbol is not None:
                    model.setData(index, symbol.value, Qt.EditRole)
            return True
        return super().editorEvent(event, model, option, index)

    def setEditorData(self, editor, index):
        pass

    def setModelData(self, editor, model, index):
        pass


class WaypointTable(QWidget):
    def __init__(self, appctxt: Any, waypoint_table: QTableWidget, parent: QWidget) -> None:
        super().__init__(parent)
        self.waypoint_table: QTableWidget = waypoint_table
        self.parent_widget: QWidget = parent
        self.appctxt: Any = appctxt
        self.logger = logger.Logger.get_logger()
        self._waypoints: List[WaypointData] = []
        self.float_delegate = FloatDelegate()
        self.datetime_delegate = DateTimeDelegate()
        self.setup_waypoint_table()

    @property
    def waypoints(self) -> List[WaypointData]:
        return self._waypoints

    @waypoints.setter
    def waypoints(self, new_waypoints: List[WaypointData]) -> None:
        self._waypoints = self.reindex_waypoints(new_waypoints)
        self.refresh_waypoint_table()

    def setup_waypoint_table(self) -> None:
        headers: List[str] = [name for name in TableColumn.__members__.keys()]
        self.waypoint_table.setHorizontalHeaderLabels(headers)
        self.waypoint_table.setItemDelegateForColumn(  # Name
            TableColumn.LATITUDE.value, FloatDelegate(decimals=6, parent=self)
        )
        self.waypoint_table.setItemDelegateForColumn(  # Longitude
            TableColumn.LONGITUDE.value, FloatDelegate(decimals=6, parent=self)
        )
        self.waypoint_table.setItemDelegateForColumn(  # Altitude
            TableColumn.ALTITUDE.value, AltitudeDelegate(parent=self)
        )
        self.waypoint_table.setItemDelegateForColumn(  # Timestamp
            TableColumn.TIMESTAMP.value, DateTimeDelegate(parent=self)
        )
        self.waypoint_table.setItemDelegateForColumn(  # Symbol
            TableColumn.SYMBOL.value, SymbolDelegate(self.appctxt, parent=self)
        )
        self.waypoint_table.setItemDelegateForColumn(  # Description
            TableColumn.DESCRIPTION.value, DescriptionDelegate(parent=self)
        )

        header: QHeaderView = self.waypoint_table.horizontalHeader()
        for i in range(self.waypoint_table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(
            TableColumn.DESCRIPTION.value, QHeaderView.Stretch
        )  # Description
        self.waypoint_table.horizontalHeader().setStretchLastSection(True)
        self.waypoint_table.cellChanged.connect(self.slot_waypoint_data_changed)

    def refresh_waypoint_table(self) -> None:
        self.waypoint_table.blockSignals(True)
        self.waypoint_table.setRowCount(0)  # Clear existing rows
        self.waypoint_table.setRowCount(len(self._waypoints))
        for row_idx, wp_data in enumerate(self._waypoints):
            self.set_table_row_from_wp_data(row_idx, wp_data)
        self.waypoint_table.blockSignals(False)

    def set_table_row_from_wp_data(
        self,
        row_idx: int,
        wp_data: WaypointData,
    ) -> None:
        self.waypoint_table.setItem(row_idx, 0, QTableWidgetItem(wp_data.name or ""))
        self.waypoint_table.setItem(
            row_idx,
            TableColumn.LATITUDE.value,
            QTableWidgetItem(
                f"{wp_data.latitude:.6f}" if wp_data.latitude is not None else "0.000000"
            ),
        )
        self.waypoint_table.setItem(
            row_idx,
            TableColumn.LONGITUDE.value,
            QTableWidgetItem(
                f"{wp_data.longitude:.6f}" if wp_data.longitude is not None else "0.000000"
            ),
        )
        alt_item = QTableWidgetItem()
        if wp_data.altitude is not None:
            alt_item.setData(Qt.EditRole, int(wp_data.altitude))
        else:
            alt_item.setData(Qt.EditRole, 0)  # Or some placeholder for None
        alt_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.waypoint_table.setItem(row_idx, TableColumn.ALTITUDE.value, alt_item)

        ts_str: str = (
            wp_data.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            if wp_data.timestamp
            else datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        )
        self.waypoint_table.setItem(row_idx, TableColumn.TIMESTAMP.value, QTableWidgetItem(ts_str))
        symbol_item: QTableWidgetItem = QTableWidgetItem()
        symbol_display_text: str = "N/A"
        symbol_display_tooltip: str = "N/A"
        icon_path: Optional[str] = None

        if wp_data.symbol is not None:
            try:
                symbol_enum: MapSymbol = MapSymbol(wp_data.symbol)
                symbol_display_text = f"{symbol_enum.value}"
                symbol_display_tooltip = f"{symbol_enum.name.lower()}"
                icon_file_name: str = f"{symbol_enum.name.lower()}.png"
                icon_path = str(Path("wpt_icons") / icon_file_name)
            except ValueError:
                symbol_display_text = f"{wp_data.symbol} (Unknown)"

        symbol_item.setText(symbol_display_text)
        symbol_item.setToolTip(symbol_display_tooltip)
        if icon_path:
            resolved_icon_path: str = get_resource_path(self.appctxt, icon_path)
            icon: QIcon = QIcon(resolved_icon_path)
            if not icon.isNull():
                symbol_item.setIcon(icon)
            else:
                self.logger.warning(
                    f"Warning: Icon not found for symbol {symbol_display_text} at {resolved_icon_path}"
                )
        self.waypoint_table.setItem(row_idx, TableColumn.SYMBOL.value, symbol_item)
        self.waypoint_table.setItem(
            row_idx, TableColumn.DESCRIPTION.value, QTableWidgetItem(wp_data.description or "")
        )

    def _get_selected_table_rows(self) -> List[int]:
        return sorted(set(item.row() for item in self.waypoint_table.selectedItems()), reverse=True)

    def reindex_waypoints(self, waypoints_data: List[WaypointData]) -> List[WaypointData]:
        for idx, wp in enumerate(waypoints_data):
            wp.message_index = idx
        return waypoints_data

    @Slot()
    def slot_add_waypoint(self) -> None:
        new_wp = WaypointData(message_index=len(self._waypoints))
        self._waypoints.append(new_wp)
        self.refresh_waypoint_table()
        new_row_index = len(self._waypoints) - 1
        if new_row_index >= 0:
            self.waypoint_table.selectRow(new_row_index)
            self.waypoint_table.scrollToItem(self.waypoint_table.item(new_row_index, 0))

    @Slot()
    def slot_delete_selected_waypoints(self) -> None:
        selected_rows: List[int] = self._get_selected_table_rows()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select waypoint(s) to delete.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete {len(selected_rows)} waypoint(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if reply == QMessageBox.StandardButton.Yes:
            rows_to_delete = sorted(set(selected_rows), reverse=True)
            num_deleted = 0
            for row_idx in rows_to_delete:
                if 0 <= row_idx < len(self._waypoints):
                    del self._waypoints[row_idx]
                    num_deleted += 1

            self.waypoints = self.waypoints

            if num_deleted > 0:
                self.logger.log(f"Deleted {num_deleted} waypoint(s).")

    @Slot(int, int)
    def slot_waypoint_data_changed(self, row: int, column: int) -> None:
        self.logger.log(f"Waypoint data changed at row {row}, column {column}.")
        if row < 0 or row >= len(self._waypoints):
            self.logger.error(f"Waypoint data change for invalid row: {row}")
            return

        wp_data: WaypointData = self._waypoints[row]
        item: Optional[QTableWidgetItem] = self.waypoint_table.item(row, column)
        if not item:
            return

        new_value: Any = None
        try:
            if column == TableColumn.NAME.value:
                new_value = item.text()
                wp_data.name = new_value
            elif column == TableColumn.LATITUDE.value:
                new_value = float(item.text())
                wp_data.latitude = new_value
            elif column == TableColumn.LONGITUDE.value:
                new_value = float(item.text())
                wp_data.longitude = new_value
            elif column == TableColumn.ALTITUDE.value:
                new_value = int(item.text())
                wp_data.altitude = new_value
            elif column == TableColumn.TIMESTAMP.value:
                cell_widget = self.waypoint_table.cellWidget(row, column)
                if isinstance(cell_widget, QDateTimeEdit):
                    new_value = cell_widget.dateTime().toPython().replace(tzinfo=timezone.utc)
                    wp_data.timestamp = new_value
                else:
                    new_value = (
                        QDateTime.fromString(item.text(), Qt.ISODateWithMs)
                        .toPython()
                        .replace(tzinfo=timezone.utc)
                    )
                    wp_data.timestamp = new_value
            elif column == TableColumn.SYMBOL.value:
                new_value = int(item.text())
                wp_data.symbol = new_value

                self.waypoint_table.blockSignals(True)
                symbol_item = self.waypoint_table.item(row, TableColumn.SYMBOL.value)
                if symbol_item:
                    try:
                        symbol_enum = MapSymbol(wp_data.symbol)
                        icon_file_name = f"{symbol_enum.name.lower()}.png"
                        icon_path = str(Path("wpt_icons") / icon_file_name)
                        resolved_icon_path = get_resource_path(self.appctxt, icon_path)
                        icon = QIcon(resolved_icon_path)
                        if not icon.isNull():
                            symbol_item.setIcon(icon)
                        else:
                            symbol_item.setIcon(QIcon())
                            self.logger.warning(
                                f"Warning: Icon not found for symbol {symbol_enum.value} at {resolved_icon_path}"
                            )
                        symbol_item.setText(f"{symbol_enum.value}")
                        symbol_item.setToolTip(symbol_enum.name.lower())
                    except Exception:
                        symbol_item.setIcon(QIcon())
                        symbol_item.setText(f"{wp_data.symbol} (Unknown)")
                        symbol_item.setToolTip("N/A")
                self.waypoint_table.blockSignals(False)

            elif column == TableColumn.DESCRIPTION.value:
                new_value = item.text()
                wp_data.description = new_value
            else:
                return

            self.logger.log(
                f"Waypoint '{wp_data.name}' (idx {row}), field '{self.waypoint_table.horizontalHeaderItem(column).text()}' changed to: {new_value}"
            )

        except ValueError as e:
            self.logger.error(
                f"Invalid data for row {row}, col {column}: {item.text()}. Error: {e}"
            )
            QMessageBox.warning(
                self, "Edit Error", f"Invalid value entered: {e}. Please try again."
            )
            self.refresh_waypoint_table()
