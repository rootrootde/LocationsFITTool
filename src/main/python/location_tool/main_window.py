from typing import Any, List, Optional

from fit_tool.profile.profile_type import LocationSettings as FitLocationSettingsEnum
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QWidget,
)

from .fit.fit import FitFileHandler
from .fit.fit_data import (
    FileCreatorMessageData,
    FileIdMessageData,
    LocationSettingsMessageData,
    LocationsFitFileData,
)
from .gpx.gpx import GpxFileHandler
from .ui_layouts.ui_main_window import Ui_MainWindow
from .utils import logger
from .waypoints.table import WaypointTableController


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, appctxt: Any, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.appctxt = appctxt
        self.logger = logger.Logger.get_logger(self.log_textedit)
        self.fit_handler = FitFileHandler(appctxt)
        self.gpx_handler = GpxFileHandler(appctxt)

        self.resizeDocks([self.log_dock], [150], Qt.Vertical)

        # Sync toggle action with log dock visibility
        self.toggle_debug_log_action.setChecked(self.log_dock.isVisible())

        # add all actions to the main window to enable shortcuts
        for action in self.findChildren(QAction):
            if isinstance(action, QAction):  # Ensure it's a QAction
                self.addAction(action)

        self.loaded_location_settings: Optional[FitLocationSettingsEnum] = None
        self.current_file_path: Optional[str] = None

        # Setup the waypoint table
        self.waypoint_table_controller = WaypointTableController(
            self.waypoint_table, self, self.appctxt
        )

        # Connect actions to slots
        self.import_locations_fit_action.triggered.connect(self.slot_import_locations_fit)
        self.import_gpx_action.triggered.connect(self.slot_import_gpx)
        self.save_locations_fit_action.triggered.connect(self.slot_save_locations_fit)

        self.add_wpt_action.triggered.connect(self.waypoint_table_controller.slot_add_waypoint)
        self.delete_wpt_action.triggered.connect(
            self.waypoint_table_controller.slot_delete_selected_waypoints
        )
        self.toggle_debug_log_action.toggled.connect(self.slot_toggle_log_dock)
        self.log_dock.visibilityChanged.connect(self.toggle_debug_log_action.setChecked)

        self.delete_all_wpts_action.triggered.connect(
            self.waypoint_table_controller.slot_delete_all_waypoints
        )

        self.waypoint_table_controller.setup_waypoint_table()

        self.logger.log("Application started.")

    @Slot()
    def slot_import_locations_fit(self) -> None:
        file_path: Optional[str]
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Locations.fit File", "", "FIT Files (*.fit)"
        )
        if not file_path:
            return

        try:
            fit_file_data_container = self.fit_handler.parse_fit_file(
                file_path, logger=self.logger.log
            )
            if fit_file_data_container.errors:
                for error in fit_file_data_container.errors:
                    self.logger.warning(f"FIT Read Warning: {error}")
                    QMessageBox.warning(self, "FIT Read Warning", str(error))

            self.current_file_path = file_path

            self.waypoint_table_controller.waypoints = (
                self.waypoint_table_controller.waypoints + fit_file_data_container.locations
            )

            self.logger.log(
                f"Successfully imported and appended from GPX file: {file_path}. Waypoints added: {len(fit_file_data_container.locations)}"
            )

        except Exception as e:
            self.logger.error(f"Failed to import FIT file: {e}")
            QMessageBox.critical(self, "Import Error", f"Could not import FIT file: {e}")

    @Slot()
    def slot_import_gpx(self) -> None:
        file_path: Optional[str]
        file_path, _ = QFileDialog.getOpenFileName(self, "Import GPX File", "", "GPX Files (*.gpx)")
        if not file_path:
            return

        try:
            waypoints, errors = self.gpx_handler.parse_gpx_file(file_path, logger=self.logger.log)
            if errors:
                for error in errors:
                    self.logger.warning(f"GPX Read Error/Warning: {error}")
                    QMessageBox.warning(self, "GPX Read Warning", str(error))

            self.current_file_path = file_path
            self.waypoint_table_controller.waypoints = (
                self.waypoint_table_controller.waypoints + waypoints
            )

            self.logger.log(
                f"Successfully imported and appended from GPX file: {file_path}. Waypoints added: {len(waypoints)}"
            )

        except Exception as e:
            self.logger.error(f"Failed to import GPX file: {e}")
            QMessageBox.critical(self, "Import Error", f"Could not import GPX file: {e}")

    @Slot()
    def slot_save_locations_fit(self) -> None:
        from location_tool.save_fit_dialog import SaveFitDialog

        current_waypoints = self.waypoint_table_controller.waypoints
        if not current_waypoints:
            QMessageBox.information(self, "No Data", "There are no waypoints to save.")
            return

        dlg = SaveFitDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return

        file_path = dlg.get_save_path()
        if not file_path:
            QMessageBox.warning(self, "No Path", "Please select a save path.")
            return

        mode_str = dlg.get_mode()

        mode_enum = FitLocationSettingsEnum[mode_str]

        fit_data_container = LocationsFitFileData(
            file_id=FileIdMessageData(),
            creator=FileCreatorMessageData(),
            location_settings=LocationSettingsMessageData(location_settings_enum=mode_enum),
            locations=current_waypoints,
        )

        try:
            success: bool
            warnings: List[str]
            critical_errors: List[str]

            # Save the FIT file using the fit_handler
            success, warnings, critical_errors = self.fit_handler.write_fit_file(
                file_path, fit_data_container
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
