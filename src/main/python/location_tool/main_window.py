from datetime import timezone  # Added import
from typing import Any, Callable, List, Optional

from fit_tool.profile.profile_type import LocationSettings as FitLocationSettingsEnum
from location_tool import fit_handler, logging_utils
from location_tool import settings as app_settings
from location_tool import table as table_manager
from location_tool import waypoints as waypoint_manager
from location_tool.ui_main_window import Ui_MainWindow
from PySide6.QtCore import QDateTime, Qt, Slot  # Added QDateTime
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDateTimeEdit,  # Added QDateTimeEdit
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QTableWidgetItem,  # Added QTableWidgetItem
    QWidget,
)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, appctxt: Any, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.appctxt = appctxt
        self.setupUi(self)
        self.resizeDocks([self.log_dock], [150], Qt.Vertical)

        # Initialize logger
        self.logger: logging_utils.Logger = logging_utils.Logger(
            self.log_textedit, app_name="LocationsFITTool"
        )

        # add all actions to the main window to enable shortcuts
        for action in self.findChildren(QAction):
            if isinstance(action, QAction):  # Ensure it's a QAction
                self.addAction(action)

        self.current_waypoints_data: list[fit_handler.LocationMessageData] = []
        self.loaded_location_settings: Optional[FitLocationSettingsEnum] = None
        self.current_file_path: Optional[str] = None
        self.fit_header_defaults: Optional[fit_handler.FileIdMessageData] = None
        self.fit_creator_defaults: Optional[fit_handler.FileCreatorMessageData] = None

        # Populate the existing Location Settings ComboBox from the UI
        for setting in FitLocationSettingsEnum:
            self.location_settings_combo.addItem(setting.name, setting)

        # Connect actions to slots
        self.import_locations_fit_action.triggered.connect(self.slot_import_locations_fit)
        self.import_gpx_action.triggered.connect(self.slot_import_gpx)
        self.save_locations_fit_action.triggered.connect(self.slot_save_locations_fit)
        self.add_wpt_action.triggered.connect(self.slot_add_waypoint)
        self.delete_wpt_action.triggered.connect(self.slot_delete_selected_waypoints)
        self.delete_all_wpts_action.triggered.connect(self.slot_delete_all_waypoints)
        self.toggle_debug_log_action.toggled.connect(self.slot_toggle_log_dock)

        self._load_fit_header_defaults()
        self._load_fit_creator_defaults()

        self._setup_waypoint_table()
        self._populate_waypoint_table()

        self.logger.log("Application started.")

    def _import_fit_file(self, logger: Callable[[str], None] = print) -> None:
        file_path: Optional[str]
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Locations.fit File", "", "FIT Files (*.fit)"
        )
        if not file_path:
            return

        try:
            fit_file_data_container = fit_handler.read_fit_file(file_path, logger=self.logger.log)
            if fit_file_data_container.errors:
                for error in fit_file_data_container.errors:
                    self.logger.warning(f"FIT Read Warning: {error}")
                    QMessageBox.warning(self, "FIT Read Warning", str(error))

            self.current_file_path = file_path
            self.current_waypoints_data.extend(fit_file_data_container.locations)
            self.current_waypoints_data = waypoint_manager.reindex_waypoints(
                self.current_waypoints_data
            )  # Re-index

            # Only update location settings if the imported FIT file has them
            if (
                fit_file_data_container.location_settings
                and fit_file_data_container.location_settings.location_settings_enum is not None
            ):
                self.loaded_location_settings = (
                    fit_file_data_container.location_settings.location_settings_enum
                )
                index = self.location_settings_combo.findData(self.loaded_location_settings)
                if index >= 0:
                    self.location_settings_combo.setCurrentIndex(index)

            self._populate_waypoint_table()

            if fit_file_data_container.header:
                self.fit_header_defaults = fit_file_data_container.header
            if fit_file_data_container.creator:
                self.fit_creator_defaults = fit_file_data_container.creator

            self.logger.log(f"Successfully imported and appended from FIT file: {file_path}")

        except Exception as e:
            self.logger.error(f"Failed to import FIT file: {e}")
            QMessageBox.critical(self, "Import Error", f"Could not import FIT file: {e}")

    def _import_gpx_file(self, logger: Callable[[str], None] = print) -> None:
        file_path: Optional[str]
        file_path, _ = QFileDialog.getOpenFileName(self, "Import GPX File", "", "GPX Files (*.gpx)")
        if not file_path:
            return

        try:
            waypoints, errors = fit_handler.read_gpx_file(file_path, logger=self.logger.log)
            if errors:
                for error in errors:
                    self.logger.warning(f"GPX Read Error/Warning: {error}")
                    QMessageBox.warning(self, "GPX Read Warning", str(error))

            self.current_file_path = file_path
            self.current_waypoints_data.extend(waypoints)
            self.current_waypoints_data = waypoint_manager.reindex_waypoints(
                self.current_waypoints_data
            )  # Re-index
            self._populate_waypoint_table()
            self.logger.log(
                f"Successfully imported and appended from GPX file: {file_path}. Waypoints added: {len(waypoints)}"
            )

        except Exception as e:
            self.logger.error(f"Failed to import GPX file: {e}")
            QMessageBox.critical(self, "Import Error", f"Could not import GPX file: {e}")

    def _save_fit_file(
        self,
        file_path: str,
        fit_data_container: fit_handler.LocationsFitFileData,
        logger: Callable[[str], None] = print,
    ) -> bool:
        try:
            success: bool
            warnings: List[str]
            critical_errors: List[str]
            success, warnings, critical_errors = fit_handler.write_fit_file(
                file_path, fit_data_container, logger=self.logger.log
            )
            if critical_errors:
                for error in critical_errors:
                    self.logger.error(f"Critical FIT Save Error: {error}")
                    QMessageBox.critical(self, "FIT Save Error", str(error))
                return False

            if warnings:
                for warning in warnings:
                    self.logger.warning(f"FIT Save Warning: {warning}")
                    QMessageBox.warning(self, "FIT Save Warning", str(warning))

            if success:
                self.logger.log(f"File saved successfully to {file_path}")
                QMessageBox.information(
                    self,
                    "Save Successful",
                    f"File saved successfully to {file_path}",
                )
                self.current_file_path = file_path
            return success

        except Exception as e:
            self.logger.error(f"Failed to save FIT file: {e}")
            QMessageBox.critical(self, "Save Error", f"Could not save FIT file: {e}")
            return False

    def _get_selected_table_rows(self) -> List[int]:
        return sorted([item.row() for item in self.waypoint_table.selectedItems()], reverse=True)

    def _load_fit_header_defaults(self) -> None:
        self.fit_header_defaults = app_settings.load_fit_header_defaults()
        if self.fit_header_defaults:
            self.logger.log("Loaded FIT header defaults from settings.")
        else:
            self.logger.log(
                "No FIT header defaults found in settings, will use hardcoded defaults if needed."
            )
            self.fit_header_defaults = fit_handler.FileIdMessageData()

    def _load_fit_creator_defaults(self) -> None:
        self.fit_creator_defaults = app_settings.load_fit_creator_defaults()
        if self.fit_creator_defaults:
            self.logger.log("Loaded FIT creator defaults from settings.")
        else:
            self.logger.log(
                "No FIT creator defaults found in settings, will use hardcoded defaults if needed."
            )
            self.fit_creator_defaults = fit_handler.FileCreatorMessageData()

    def _save_fit_header_defaults(self, header: Optional[fit_handler.FileIdMessageData]) -> None:
        app_settings.save_fit_header_defaults(header)
        if header:
            self.logger.log("Saved FIT header defaults to settings.")
        else:
            self.logger.log("Cleared FIT header defaults from settings.")

    def _save_fit_creator_defaults(
        self, creator: Optional[fit_handler.FileCreatorMessageData]
    ) -> None:
        app_settings.save_fit_creator_defaults(creator)
        if creator:
            self.logger.log("Saved FIT creator defaults to settings.")
        else:
            self.logger.log("Cleared FIT creator defaults from settings.")

    def _get_fit_header_for_save(self) -> fit_handler.FileIdMessageData:
        if self.fit_header_defaults:
            return self.fit_header_defaults
        return fit_handler.FileIdMessageData()

    def _get_fit_creator_for_save(self) -> fit_handler.FileCreatorMessageData:
        if self.fit_creator_defaults:
            return self.fit_creator_defaults
        return fit_handler.FileCreatorMessageData()

    def _setup_waypoint_table(self) -> None:
        table_manager.setup_waypoint_table(self.waypoint_table, self)
        self.waypoint_table.cellChanged.connect(self.slot_waypoint_data_changed)

    def _populate_waypoint_table(self) -> None:
        try:
            self.waypoint_table.cellChanged.disconnect(self.slot_waypoint_data_changed)
        except RuntimeError:
            pass

        table_manager.populate_waypoint_table(
            self.waypoint_table, self.current_waypoints_data, self.appctxt, self.logger.log
        )
        self.waypoint_table.cellChanged.connect(self.slot_waypoint_data_changed)

    def _clear_all_forms_and_tables(self) -> None:
        self.current_waypoints_data = []
        self.loaded_location_settings = None
        self.current_file_path = None
        self._populate_waypoint_table()
        self.location_settings_combo.setCurrentIndex(-1)
        self.logger.log("Cleared all waypoint data and current file information.")

    @Slot()
    def slot_import_locations_fit(self) -> None:
        self._import_fit_file(logger=self.logger.log)

    @Slot()
    def slot_import_gpx(self) -> None:
        self._import_gpx_file(logger=self.logger.log)

    @Slot()
    def slot_save_locations_fit(self) -> None:
        if not self.current_waypoints_data:
            QMessageBox.information(self, "No Data", "There are no waypoints to save.")
            return

        default_filename: str = "locations.fit"
        if self.current_file_path:
            default_filename = self.current_file_path.split("/")[-1]
            if not default_filename.lower().endswith(".fit"):
                default_filename = "locations.fit"

        file_path: Optional[str]
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Locations FIT File", default_filename, "FIT Files (*.fit)"
        )

        if not file_path:
            return

        if not file_path.lower().endswith(".fit"):
            file_path += ".fit"

        header_data = self._get_fit_header_for_save()
        creator_data = self._get_fit_creator_for_save()

        selected_location_setting_enum: Optional[FitLocationSettingsEnum] = (
            self.location_settings_combo.currentData()
        )
        location_setting_data = fit_handler.LocationSettingsMessageData(
            location_settings_enum=selected_location_setting_enum
        )

        fit_data_container = fit_handler.LocationsFitFileData(
            header=header_data,
            creator=creator_data,
            location_settings=location_setting_data,
            locations=self.current_waypoints_data,
        )

        if self._save_fit_file(file_path, fit_data_container, logger=self.logger.log):
            pass

    @Slot()
    def slot_add_waypoint(self) -> None:
        new_wp: Optional[fit_handler.LocationMessageData]
        self.current_waypoints_data, new_wp = waypoint_manager.add_waypoint(
            self.current_waypoints_data
        )
        self._populate_waypoint_table()
        if new_wp:
            last_row = self.waypoint_table.rowCount() - 1
            if last_row >= 0:
                self.waypoint_table.selectRow(last_row)
                self.waypoint_table.scrollToItem(self.waypoint_table.item(last_row, 0))
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
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            num_deleted: int
            new_selection_row: int
            (
                self.current_waypoints_data,
                num_deleted,
                new_selection_row,
            ) = waypoint_manager.delete_waypoints(self.current_waypoints_data, selected_rows)
            self._populate_waypoint_table()

            if self.current_waypoints_data and new_selection_row != -1:
                if new_selection_row < self.waypoint_table.rowCount():
                    self.waypoint_table.selectRow(new_selection_row)
            self.logger.log(f"Deleted {num_deleted} waypoint(s).")

    @Slot()
    def slot_delete_all_waypoints(self) -> None:
        if not self.current_waypoints_data:
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
            self.current_waypoints_data = waypoint_manager.delete_all_waypoints()
            self._populate_waypoint_table()
            self.logger.log("Deleted all waypoints.")

    @Slot(int, int)
    def slot_waypoint_data_changed(self, row: int, column: int) -> None:
        self.logger.log(f"Waypoint data changed at row {row}, column {column}.")
        if row < 0 or row >= len(self.current_waypoints_data):
            self.logger.error(f"Waypoint data change for invalid row: {row}")
            return

        wp_data: fit_handler.LocationMessageData = self.current_waypoints_data[row]
        item: Optional[QTableWidgetItem] = self.waypoint_table.item(
            row, column
        )  # QTableWidgetItem can be None
        if not item:
            return

        new_value: Any = None
        try:
            if column == 0:
                new_value = item.text()
                wp_data.name = new_value
            elif column == 1:
                new_value = float(item.text())
                wp_data.latitude = new_value
            elif column == 2:
                new_value = float(item.text())
                wp_data.longitude = new_value
            elif column == 3:
                new_value = float(item.text())
                wp_data.altitude = new_value
            elif column == 4:
                q_datetime_edit = self.waypoint_table.cellWidget(row, column)
                if isinstance(q_datetime_edit, QDateTimeEdit):
                    new_value = q_datetime_edit.dateTime().toPython().replace(tzinfo=timezone.utc)
                    wp_data.timestamp = new_value
                else:
                    new_value = (
                        QDateTime.fromString(item.text(), Qt.ISODateWithMs)
                        .toPython()
                        .replace(tzinfo=timezone.utc)
                    )
                    wp_data.timestamp = new_value
            elif column == 5:
                new_value = int(item.text())
                wp_data.symbol = new_value
            elif column == 6:
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
            self._populate_waypoint_table()

    @Slot(bool)
    def slot_toggle_log_dock(self, checked: bool) -> None:
        if checked:
            self.log_dock.show()
        else:
            self.log_dock.hide()
        self.logger.log(f"Log window {'shown' if checked else 'hidden'}.")

    @Slot()
    def slot_about(self) -> None:
        QMessageBox.about(
            self,
            "About LocationsFITTool",
            "LocationsFITTool\nVersion 0.1.0 (Example)\n\n"
            "A tool for managing FIT location files.\n"
            "Copyright 2024 Your Name/Company",
        )
        self.logger.log("Displayed About dialog.")

    def closeEvent(
        self, event: Any
    ) -> None:  # Consider using QCloseEvent if available and appropriate
        self.logger.log("Application closing.")
        super().closeEvent(event)
