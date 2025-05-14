from typing import Any, Callable, List, Optional

from fit_tool.profile.profile_type import LocationSettings as FitLocationSettingsEnum
from location_tool import fit_handler, logging_utils
from location_tool.table import WptTableManager
from location_tool.ui_main_window import Ui_MainWindow
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QWidget,
)


class MainWindow(QMainWindow, Ui_MainWindow):
    wpts_need_reindexing = Signal(list)

    def __init__(self, appctxt: Any, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.appctxt = appctxt

        self.setupUi(self)
        self.resizeDocks([self.log_dock], [150], Qt.Vertical)

        # Sync toggle action with log dock visibility
        self.toggle_debug_log_action.setChecked(self.log_dock.isVisible())
        self.log_dock.visibilityChanged.connect(self.toggle_debug_log_action.setChecked)

        # Initialize logger
        logging_utils.Logger.init(self.log_textedit, app_name="LocationsFITTool")
        self.logger = logging_utils.Logger.get()

        # add all actions to the main window to enable shortcuts
        for action in self.findChildren(QAction):
            if isinstance(action, QAction):  # Ensure it's a QAction
                self.addAction(action)

        self.current_waypoints_data: list[fit_handler.LocationMessageData] = []
        self.loaded_location_settings: Optional[FitLocationSettingsEnum] = None
        self.current_file_path: Optional[str] = None

        # Populate the existing Location Settings ComboBox from the UI
        for setting in FitLocationSettingsEnum:
            self.location_settings_combo.addItem(setting.name, setting)

        # Setup the waypoint table
        self.table_manager = WptTableManager(self.waypoint_table, self, self.appctxt)

        # Connect actions to slots
        self.import_locations_fit_action.triggered.connect(self.slot_import_locations_fit)
        self.import_gpx_action.triggered.connect(self.slot_import_gpx)
        self.save_locations_fit_action.triggered.connect(self.slot_save_locations_fit)

        self.add_wpt_action.triggered.connect(self.table_manager.slot_add_waypoint)
        self.delete_wpt_action.triggered.connect(self.table_manager.slot_delete_selected_waypoints)
        self.toggle_debug_log_action.toggled.connect(self.slot_toggle_log_dock)

        self.delete_all_wpts_action.triggered.connect(self.table_manager.slot_delete_all_waypoints)
        self.wpts_need_reindexing.connect(self.table_manager.reindex_waypoints)

        self.table_manager.setup_waypoint_table()
        self.table_manager.populate_waypoint_table()

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

            self.logger.log(f"Waypoints loaded: {len(self.current_waypoints_data)}")

            self.wpts_need_reindexing.emit(
                self.current_waypoints_data
            )  # Emit signal to reindex waypoints

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

            self.logger.log(f"Successfully imported and appended from FIT file: {file_path}")
            self.table_manager.populate_waypoint_table()

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

            self.wpts_need_reindexing.emit(
                self.current_waypoints_data
            )  # Emit signal to reindex waypoints

            self.table_manager.populate_waypoint_table()
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

    def _clear_all_forms_and_tables(self) -> None:
        self.current_waypoints_data = []
        self.loaded_location_settings = None
        self.current_file_path = None
        self.table_manager.populate_waypoint_table()
        self.location_settings_combo.setCurrentIndex(-1)
        self.logger.log("Cleared all waypoint data and current file information.")

    # -----------------------------------------------------
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

        default_filename: str = "Locations.fit"
        if self.current_file_path:
            default_filename = self.current_file_path.split("/")[-1]
            if not default_filename.lower().endswith(".fit"):
                default_filename = "Locations.fit"

        file_path: Optional[str]
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Locations FIT File", default_filename, "FIT Files (*.fit)"
        )

        if not file_path:
            return

        if not file_path.lower().endswith(".fit"):
            file_path += ".fit"

        header_data = fit_handler.FileIdMessageData()
        creator_data = fit_handler.FileCreatorMessageData()

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

    @Slot(bool)
    def slot_toggle_log_dock(self, checked: bool) -> None:
        if checked:
            self.log_dock.show()
        else:
            self.log_dock.hide()
        self.logger.log(f"Log window {'shown' if checked else 'hidden'}.")

    def closeEvent(
        self, event: Any
    ) -> None:  # Consider using QCloseEvent if available and appropriate
        self.logger.log("Application closing.")
        super().closeEvent(event)
