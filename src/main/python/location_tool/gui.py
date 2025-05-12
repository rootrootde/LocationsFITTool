import os
from datetime import datetime, timezone

from fit_tool.profile.profile_type import LocationSettings as FitLocationSettingsEnum
from fit_tool.profile.profile_type import MapSymbol
from location_tool import fit_handler
from location_tool.ui_main_window import Ui_MainWindow
from PySide6.QtCore import QDateTime, Qt, QTimer, Slot
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDateTimeEdit,
    QDoubleSpinBox,
    QFileDialog,
    QHeaderView,
    QMainWindow,
    QMessageBox,
    QStyledItemDelegate,
    QTableWidgetItem,
)

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


# Helper to resolve resource paths for both fbs and non-fbs usage
def get_resource_path(appctxt, relative_path):
    if appctxt:
        return appctxt.get_resource(relative_path)
    return os.path.join(BASE_PATH, "..", "resources", relative_path)


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
            editor.setRange(-5000.0, 29990.0)
            editor.setDecimals(0)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        try:
            editor.setValue(float(value))
        except (ValueError, TypeError):
            editor.setValue(0.0)

    def setModelData(self, editor, model, index):
        model.setData(index, f"{editor.value():.{self.decimals}f}", Qt.EditRole)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, appctxt, parent=None):
        super().__init__(parent)
        self.appctxt = appctxt
        self.setupUi(self)
        self.resizeDocks([self.log_dock], [100], Qt.Vertical)

        # add all actions to the main window to enable shortcuts
        for action in self.findChildren(QAction):
            self.addAction(action)

        self.current_waypoints_data: list[fit_handler.FitLocationData] = []
        self.loaded_location_settings: FitLocationSettingsEnum | None = None

        # Populate the existing Location Settings ComboBox from the UI
        for setting in FitLocationSettingsEnum:
            self.location_settings_combo.addItem(setting.name, setting)

        # Connect actions to slots
        self.import_locations_fit_action.triggered.connect(
            self.slot_import_locations_fit
        )
        self.import_gpx_action.triggered.connect(self.slot_import_gpx)
        self.save_locations_fit_action.triggered.connect(self.slot_save_locations_fit)
        self.add_wpt_action.triggered.connect(self.slot_add_waypoint)
        self.delete_wpt_action.triggered.connect(self.slot_delete_selected_waypoint)
        self.delete_all_wpts_action.triggered.connect(self.slot_delete_all_waypoints)

        # keep action state in sync with the log_dock visibility
        self.toggle_debug_log_action.setChecked(self.log_dock.isVisible())
        self.log_dock.visibilityChanged.connect(self.toggle_debug_log_action.setChecked)

        self._setup_waypoints_table()
        self._clear_all_forms_and_tables()

    def _setup_waypoints_table(self):
        self.waypoint_table.setColumnCount(7)  # Changed from 8 to 7
        headers = [
            "Name",
            "Latitude",
            "Longitude",
            "Altitude",
            "Timestamp",
            "Symbol",
            "Description",
        ]
        self.waypoint_table.setHorizontalHeaderLabels(headers)
        self.waypoint_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.waypoint_table.setEditTriggers(
            QAbstractItemView.DoubleClicked
            | QAbstractItemView.SelectedClicked
            | QAbstractItemView.EditKeyPressed
        )
        # Adjust column indices for delegates
        self.waypoint_table.setItemDelegateForColumn(
            1, FloatDelegate(decimals=6, parent=self)
        )  # Latitude
        self.waypoint_table.setItemDelegateForColumn(
            2, FloatDelegate(decimals=6, parent=self)
        )  # Longitude
        self.waypoint_table.setItemDelegateForColumn(
            3, FloatDelegate(decimals=2, parent=self)
        )  # Altitude
        self.waypoint_table.setItemDelegateForColumn(
            4, DateTimeDelegate(parent=self)
        )  # Timestamp

        # Column resizing strategy - adjust indices
        header = self.waypoint_table.horizontalHeader()
        # Default resize to contents for all, then stretch specific ones
        for i in range(self.waypoint_table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        header.setSectionResizeMode(6, QHeaderView.Stretch)  # Description

        # To make the table take the full width initially and on resize:
        self.waypoint_table.horizontalHeader().setStretchLastSection(True)

    def _populate_waypoints_table(self):
        self.waypoint_table.setRowCount(0)
        self.waypoint_table.setRowCount(len(self.current_waypoints_data))
        for row_idx, wp_data in enumerate(self.current_waypoints_data):
            self._set_table_row_from_wp_data(row_idx, wp_data)
        self.waypoint_table.resizeColumnsToContents()

    def _set_table_row_from_wp_data(
        self, row_idx: int, wp_data: fit_handler.FitLocationData
    ):
        self.waypoint_table.setItem(row_idx, 0, QTableWidgetItem(wp_data.name or ""))
        self.waypoint_table.setItem(
            row_idx,
            1,
            QTableWidgetItem(
                f"{wp_data.latitude:.6f}"
                if wp_data.latitude is not None
                else "0.000000"
            ),
        )
        self.waypoint_table.setItem(
            row_idx,
            2,
            QTableWidgetItem(
                f"{wp_data.longitude:.6f}"
                if wp_data.longitude is not None
                else "0.000000"
            ),
        )
        self.waypoint_table.setItem(
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
        self.waypoint_table.setItem(row_idx, 4, QTableWidgetItem(ts_str))  # Timestamp

        symbol_item = QTableWidgetItem()
        symbol_display_text = "N/A"
        symbol_display_tooltip = "N/A"
        icon_path = None

        if wp_data.symbol is not None:
            try:
                symbol_enum = MapSymbol(wp_data.symbol)
                symbol_display_text = f"{symbol_enum.value}"
                symbol_display_tooltip = f"{symbol_enum.name.lower()}"

                # Construct icon path from enum name
                icon_file_name = f"{symbol_enum.name.lower()}.png"
                icon_path = os.path.join(BASE_PATH, "icons", icon_file_name)

            except ValueError:
                symbol_display_text = f"{wp_data.symbol} (Unknown)"

        symbol_item.setText(symbol_display_text)
        symbol_item.setToolTip(symbol_display_tooltip)

        if icon_path:
            resolved_icon_path = get_resource_path(self.appctxt, icon_path)
            icon = QIcon(resolved_icon_path)
            if not icon.isNull():  # Check if icon was loaded successfully
                symbol_item.setIcon(icon)
            else:
                self.log_message(
                    f"Warning: Icon not found for symbol {symbol_display_text} at {resolved_icon_path}"
                )

        self.waypoint_table.setItem(row_idx, 5, symbol_item)  # Symbol column

        self.waypoint_table.setItem(
            row_idx,
            6,
            QTableWidgetItem(wp_data.description or ""),
        )

    def _clear_all_forms_and_tables(self):
        self.current_waypoints_data = []
        self.loaded_location_settings = None
        if self.location_settings_combo.count() > 0:
            self.location_settings_combo.setCurrentIndex(0)
        self.waypoint_table.setRowCount(0)
        self.log_textedit.clear()

    def log_message(self, message: str):
        # self.log_textedit is guaranteed to exist
        self.log_textedit.appendPlainText(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
        )
        # Auto-scroll to the bottom
        scrollbar = self.log_textedit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    @Slot()
    def slot_import_locations_fit(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Locations.fit File", "", "FIT Files (*.fit);;All Files (*)"
        )
        if file_path:
            self.log_message(f"Opening {file_path}...")
            # Do not clear all forms and tables, append instead
            fit_file_data_container = fit_handler.read_fit_file(file_path)

            if fit_file_data_container.errors:
                errors_str = "\n".join(fit_file_data_container.errors)
                QMessageBox.warning(
                    self,
                    "Warning Reading FIT File",
                    f"Encountered issues reading {file_path}:\n{errors_str}\n\nSome data may be incomplete or missing.",
                )
                self.log_message(
                    f"Warning reading {file_path}. Some data may be missing."
                )
            else:
                self.log_message(f"Successfully opened {file_path}.")

            # Append new waypoints to existing ones
            new_waypoints = fit_file_data_container.waypoints
            if new_waypoints:
                current_max_idx = (
                    max(wp.message_index for wp in self.current_waypoints_data)
                    if self.current_waypoints_data
                    and any(
                        wp.message_index is not None
                        for wp in self.current_waypoints_data
                    )
                    else -1
                )
                for i, wp in enumerate(new_waypoints):
                    wp.message_index = current_max_idx + 1 + i
                    self.current_waypoints_data.append(wp)

            # Update settings from the newly imported FIT file
            if fit_file_data_container.settings:
                self.loaded_location_settings = (
                    fit_file_data_container.settings.waypoint_setting
                )
                if self.loaded_location_settings:
                    idx = self.location_settings_combo.findData(
                        self.loaded_location_settings
                    )
                    if idx >= 0:
                        self.location_settings_combo.setCurrentIndex(idx)
                elif self.location_settings_combo.count() > 0:
                    # Default to ADD if settings are not found in the imported file
                    default_setting = FitLocationSettingsEnum.ADD
                    default_idx = self.location_settings_combo.findData(default_setting)
                    if default_idx >= 0:
                        self.location_settings_combo.setCurrentIndex(default_idx)
                    else:  # Fallback
                        self.location_settings_combo.setCurrentIndex(0)

            self._reindex_waypoints()  # Re-index after appending
            self._populate_waypoints_table()
            self.log_message(
                f"Imported and appended {len(new_waypoints)} waypoints from {file_path}. Total waypoints: {len(self.current_waypoints_data)}."
            )

    @Slot()
    def slot_import_gpx(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import GPX File", "", "GPX Files (*.gpx);;All Files (*)"
        )
        if file_path:
            self.log_message(f"Importing GPX {file_path}...")
            try:
                gpx_waypoints = fit_handler.read_gpx_file(file_path)
                if not gpx_waypoints:
                    self.log_message(f"No waypoints found in {file_path}.")
                    return

                if not self.current_waypoints_data:
                    self.current_waypoints_data = gpx_waypoints
                else:
                    current_max_idx = (
                        max(wp.message_index for wp in self.current_waypoints_data)
                        if self.current_waypoints_data
                        else -1
                    )
                    for i, wp in enumerate(gpx_waypoints):
                        wp.message_index = current_max_idx + 1 + i
                        self.current_waypoints_data.append(wp)

                self._reindex_waypoints()
                self._populate_waypoints_table()
                self.log_message(
                    f"Successfully imported {len(gpx_waypoints)} waypoints from {file_path}."
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "GPX Import Error", f"Could not import GPX file: {e}"
                )
                self.log_message(f"Error importing GPX: {e}")

    def _reindex_waypoints(self):
        for i, wp in enumerate(self.current_waypoints_data):
            wp.message_index = i

    @Slot()
    def slot_save_locations_fit(self):
        if not self.current_waypoints_data:
            reply = QMessageBox.question(
                self,
                "No Waypoints",
                "There are no waypoints in the table. Do you want to save an empty Locations.fit file?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                self.log_message("Save cancelled by user.")
                return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Locations.fit File",
            "Locations_New.fit",
            "FIT Files (*.fit);;All Files (*)",
        )
        if file_path:
            self.log_message(f"Saving to {file_path}...")
            # Read data from table before clearing self.current_waypoints_data
            table_waypoints_data = []
            for row in range(self.waypoint_table.rowCount()):
                try:
                    name = self.waypoint_table.item(row, 0).text()
                    lat_str = self.waypoint_table.item(row, 1).text()
                    lon_str = self.waypoint_table.item(row, 2).text()
                    alt_str = self.waypoint_table.item(row, 3).text()
                    ts_str = self.waypoint_table.item(row, 4).text()
                    sym_full_str = self.waypoint_table.item(row, 5).text()
                    desc = self.waypoint_table.item(row, 6).text()

                    # Parse symbol - expecting format "value (name)" or just value
                    sym_val = 0  # Default
                    if sym_full_str and sym_full_str != "N/A":
                        try:
                            sym_val = int(sym_full_str.split()[0])
                        except (ValueError, IndexError):
                            self.log_message(
                                f"Could not parse symbol '{sym_full_str}' at row {row + 1}. Using default 0."
                            )

                    wp_data = fit_handler.FitLocationData(
                        message_index=row,
                        name=name,
                        latitude=float(lat_str) if lat_str else 0.0,
                        longitude=float(lon_str) if lon_str else 0.0,
                        altitude=float(alt_str) if alt_str else 0.0,
                        timestamp=datetime.strptime(
                            ts_str, "%Y-%m-%d %H:%M:%S"
                        ).replace(tzinfo=timezone.utc)
                        if ts_str
                        else datetime.now(timezone.utc),
                        symbol=sym_val,
                        description=desc,
                    )
                    table_waypoints_data.append(wp_data)
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Table Data Error",
                        f"Error reading data from table row {row + 1}: {e}",
                    )
                    self.log_message(
                        f"Error preparing data for saving at row {row + 1}."
                    )
                    return

            self.current_waypoints_data = (
                table_waypoints_data  # Update internal list before saving
            )

            selected_location_setting = self.location_settings_combo.currentData()

            fit_file_data_to_save = fit_handler.LocationsFitFileData(
                header=None,  # Using hardcoded defaults in fit_handler
                creator=None,  # Using hardcoded defaults in fit_handler
                settings=fit_handler.FitLocationSettingData(
                    waypoint_setting=selected_location_setting
                ),
                waypoints=self.current_waypoints_data,
            )

            warnings, critical_errors = fit_handler.write_fit_file(
                file_path, fit_file_data_to_save
            )

            if critical_errors:
                errors_str = "\n".join(critical_errors)
                # Log all critical errors
                for err in critical_errors:
                    self.log_message(f"Critical Save Error: {err}")
                QMessageBox.critical(
                    self,
                    "Error Saving FIT File",
                    f"Could not save {file_path}:\n{errors_str}",
                )
            else:
                success_log_message = f"Successfully saved to {file_path}."
                display_message = success_log_message
                if warnings:
                    warnings_str = "\n".join(warnings)
                    # Log all warnings
                    for warn in warnings:
                        self.log_message(f"Save Warning: {warn}")
                    display_message += (
                        f"\n\nEncountered the following warnings:\n{warnings_str}"
                    )
                    QMessageBox.information(
                        self, "File Saved with Warnings", display_message
                    )
                else:
                    QMessageBox.information(self, "File Saved", display_message)
                # Log overall success regardless of warnings
                self.log_message(success_log_message)

    @Slot()
    def slot_add_waypoint(self):
        new_wp_index = len(self.current_waypoints_data)
        new_wp = fit_handler.FitLocationData(
            name=f"Waypoint {new_wp_index}",
            description="",
            latitude=0.0,
            longitude=0.0,
            altitude=0.0,
            timestamp=datetime.now(timezone.utc),
            symbol=0,
            message_index=new_wp_index,
        )
        self.current_waypoints_data.append(new_wp)

        row_count = self.waypoint_table.rowCount()
        self.waypoint_table.insertRow(row_count)
        self._set_table_row_from_wp_data(row_count, new_wp)

        self.waypoint_table.selectRow(row_count)
        self.waypoint_table.scrollToItem(
            self.waypoint_table.item(row_count, 0),
            QAbstractItemView.ScrollHint.EnsureVisible,
        )
        self.waypoint_table.editItem(self.waypoint_table.item(row_count, 0))
        self.log_message(f"Added '{new_wp.name}'. Edit details in the table.")

    @Slot()
    def slot_delete_selected_waypoint(self):
        selected_ranges = self.waypoint_table.selectedRanges()
        if not selected_ranges:
            QMessageBox.information(
                self, "No Selection", "Select waypoint(s) to delete."
            )
            return

        rows_to_delete = set()
        for sr in selected_ranges:
            for r in range(sr.topRow(), sr.bottomRow() + 1):
                rows_to_delete.add(r)

        sorted_rows = sorted(list(rows_to_delete), reverse=True)

        if not sorted_rows:
            return

        current_selection_row_after_delete = -1
        if sorted_rows:
            current_selection_row_after_delete = sorted_rows[-1]
            if (
                current_selection_row_after_delete
                >= self.waypoint_table.rowCount() - len(sorted_rows)
            ):
                current_selection_row_after_delete = (
                    self.waypoint_table.rowCount() - len(sorted_rows) - 1
                )

        for row_idx in sorted_rows:
            if 0 <= row_idx < len(self.current_waypoints_data):
                del self.current_waypoints_data[row_idx]
            self.waypoint_table.removeRow(row_idx)

        self._reindex_waypoints()
        self._populate_waypoints_table()

        if self.waypoint_table.rowCount() > 0:
            if (
                current_selection_row_after_delete >= 0
                and current_selection_row_after_delete < self.waypoint_table.rowCount()
            ):
                self.waypoint_table.selectRow(current_selection_row_after_delete)
            else:
                self.waypoint_table.selectRow(0)

        self.log_message(f"{len(sorted_rows)} waypoint(s) deleted.")

    @Slot()
    def slot_delete_all_waypoints(self):
        reply = QMessageBox.question(
            self,
            "Confirm Delete All",
            "Are you sure you want to delete all waypoints?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.current_waypoints_data = []
            self.waypoint_table.setRowCount(0)
            self.log_message("All waypoints deleted.")
