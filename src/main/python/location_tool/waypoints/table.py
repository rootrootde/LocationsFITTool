from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional

from fit_tool.profile.profile_type import MapSymbol
from PySide6.QtCore import QDateTime, QModelIndex, Qt, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDateTimeEdit,
    QDoubleSpinBox,
    QHeaderView,
    QMessageBox,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from ..fit.fit_data import LocationMessageData
from ..utils import logger
from ..utils.utils import get_resource_path


# TODO: this should be the generic interface for all waypoint data (GpxWaypointData, LocationMessageData...)
class WaypointData:
    pass


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
        editor.setDecimals(self.decimals)
        if index.column() == 1:  # Latitude
            editor.setRange(-90.0, 90.0)
        elif index.column() == 2:  # Longitude
            editor.setRange(-180.0, 180.0)
        elif index.column() == 3:  # Altitude
            editor.setRange(-500.0, 9200.0)
            editor.setDecimals(2)  # Altitude typically has 2 decimals
        return editor

    def setEditorData(self, editor: QDoubleSpinBox, index: QModelIndex) -> None:
        value: Any = index.model().data(index, Qt.EditRole)
        try:
            editor.setValue(float(value))
        except (ValueError, TypeError):
            editor.setValue(0.0)

    def setModelData(self, editor: QDoubleSpinBox, model: Any, index: QModelIndex) -> None:
        model.setData(index, f"{editor.value():.{self.decimals}f}", Qt.EditRole)


class WaypointTableController(QWidget):
    def __init__(self, waypoint_table: QTableWidget, parent: QWidget, appctxt: Any) -> None:
        super().__init__(parent)
        self.waypoint_table = waypoint_table
        self.parent = parent
        self.appctxt = appctxt
        self.logger = logger.Logger.get_logger()
        self._waypoints: List[LocationMessageData] = []
        self.setup_waypoint_table()

    @property
    def waypoints(self) -> List[LocationMessageData]:
        return self._waypoints

    @waypoints.setter
    def waypoints(self, waypoints: List[LocationMessageData]) -> None:
        self._waypoints = self.reindex_waypoints(waypoints)
        self.refresh_waypoint_table()

    def setup_waypoint_table(self) -> None:
        self.waypoint_table.setColumnCount(7)
        headers: List[str] = [name.lower() for name in TableColumn.__members__.keys()]
        self.waypoint_table.setHorizontalHeaderLabels(headers)
        self.waypoint_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.waypoint_table.setEditTriggers(
            QAbstractItemView.DoubleClicked
            | QAbstractItemView.SelectedClicked
            | QAbstractItemView.EditKeyPressed
        )
        self.waypoint_table.setItemDelegateForColumn(
            TableColumn.LATITUDE.value, FloatDelegate(decimals=6, parent=self)
        )
        self.waypoint_table.setItemDelegateForColumn(
            TableColumn.LONGITUDE.value, FloatDelegate(decimals=6, parent=self)
        )
        self.waypoint_table.setItemDelegateForColumn(
            TableColumn.ALTITUDE.value, FloatDelegate(decimals=2, parent=self)
        )
        self.waypoint_table.setItemDelegateForColumn(
            TableColumn.TIMESTAMP.value, DateTimeDelegate(parent=self)
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

        self.waypoint_table.setRowCount(0)
        self.waypoint_table.setRowCount(len(self.waypoints))
        for row_idx, wp_data in enumerate(self.waypoints):
            self.set_table_row_from_wp_data(
                row_idx,
                wp_data,
            )
        self.waypoint_table.resizeColumnsToContents()

        self.waypoint_table.blockSignals(False)

    def set_table_row_from_wp_data(
        self,
        row_idx: int,
        wp_data: LocationMessageData,
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
        self.waypoint_table.setItem(
            row_idx,
            TableColumn.ALTITUDE.value,
            QTableWidgetItem(f"{wp_data.altitude:.2f}" if wp_data.altitude is not None else "0.00"),
        )

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
                icon_path = str(Path("icons") / icon_file_name)
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

    def reindex_waypoints(
        self, waypoints_data: List[LocationMessageData]
    ) -> List[LocationMessageData]:
        """Ensure all waypoints have a sequential message_index."""
        for i, wp in enumerate(waypoints_data):
            wp.message_index = i
        return waypoints_data

    @Slot()
    def slot_add_waypoint(self) -> None:
        new_wp_index: int = len(self.waypoints)
        new_wp = LocationMessageData(
            name=f"Waypoint {new_wp_index}",
            description="",
            latitude=0.0,
            longitude=0.0,
            altitude=0.0,
            timestamp=datetime.now(timezone.utc),
            symbol=MapSymbol.FLAG_BLUE.value,  # default
            message_index=new_wp_index,  # Initial index, will be updated by reindex
        )
        self.waypoints.append(new_wp)

        if new_wp:
            last_row = self.waypoint_table.rowCount() - 1
            if last_row >= 0:
                self.waypoint_table.selectRow(last_row)
                self.waypoint_table.scrollToItem(self.waypoint_table.item(last_row, 0))

        self.waypoints = self.waypoints
        self.logger.log(f"Added new waypoint: {new_wp.name}")

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
                if 0 <= row_idx < len(self.waypoints):
                    del self.waypoints[row_idx]
                    num_deleted += 1

            self.waypoints = self.waypoints

            if num_deleted > 0:
                self.logger.log(f"Deleted {num_deleted} waypoint(s).")

    @Slot()
    def slot_delete_all_waypoints(self) -> None:
        if not self.waypoints:
            QMessageBox.information(self, "No Data", "There are no waypoints to delete.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete All",
            "Are you sure you want to delete ALL waypoints?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.waypoints = []
            self.logger.log("Deleted all waypoints.")

    @Slot(int, int)
    def slot_waypoint_data_changed(self, row: int, column: int) -> None:
        self.logger.log(f"Waypoint data changed at row {row}, column {column}.")
        if row < 0 or row >= len(self.waypoints):
            self.logger.error(f"Waypoint data change for invalid row: {row}")
            return

        wp_data: LocationMessageData = self.waypoints[row]
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
                new_value = float(item.text())
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

                # --- Update the icon in the symbol cell ---
                # TODO put in own function
                self.waypoint_table.blockSignals(True)
                symbol_item = self.waypoint_table.item(row, TableColumn.SYMBOL.value)
                if symbol_item:
                    try:
                        symbol_enum = MapSymbol(wp_data.symbol)
                        icon_file_name = f"{symbol_enum.name.lower()}.png"
                        icon_path = str(Path("icons") / icon_file_name)
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
                # ------------------------------------------

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
