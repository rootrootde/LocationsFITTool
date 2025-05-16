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

from .device.mtp import MTPDeviceManager
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
from .waypoints.table import WaypointTable


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, appctxt: Any, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.appctxt = appctxt
        self._init_logger()
        self._init_handlers()
        self._init_state()
        self._init_waypoint_table()
        self._init_mtp_device_manager()
        self._init_actions()
        self._init_log_dock()

        self.logger.log("MainWindow initialized.")
        self.logger.log("Application started.")

    def _init_logger(self):
        self.logger = logger.Logger.get_logger(self.log_textedit)

    def _init_handlers(self):
        self.fit_handler = FitFileHandler(self.appctxt)
        self.gpx_handler = GpxFileHandler(self.appctxt)

    def _init_state(self):
        self.loaded_location_settings: Optional[FitLocationSettingsEnum] = None
        self.current_file_path: Optional[str] = None
        self.scan_for_devices_action.setChecked(True)

    def _init_waypoint_table(self):
        self.waypoint_table = WaypointTable(self.waypoint_table, self, self.appctxt)
        self.waypoint_table.setup_waypoint_table()

    def _init_mtp_device_manager(self):
        self.mtp_device_manager = MTPDeviceManager(self.appctxt, self)
        self.mtp_device_manager.device_found.connect(self.slot_device_found)
        self.mtp_device_manager.device_error.connect(self.slot_device_error)

    def _init_actions(self):
        # Add all actions to the main window to enable shortcuts
        for action in self.findChildren(QAction):
            if isinstance(action, QAction):
                self.addAction(action)

        # Connect actions to slots
        self.import_locations_fit_action.triggered.connect(self.slot_import_locations_fit)
        self.import_gpx_action.triggered.connect(self.slot_import_gpx)
        self.save_locations_fit_action.triggered.connect(self.slot_save_locations_fit)
        self.add_wpt_action.triggered.connect(self.waypoint_table.slot_add_waypoint)
        self.delete_wpt_action.triggered.connect(self.waypoint_table.slot_delete_selected_waypoints)
        self.toggle_debug_log_action.toggled.connect(self.slot_toggle_log_dock)
        self.log_dock.visibilityChanged.connect(self.toggle_debug_log_action.setChecked)
        self.delete_all_wpts_action.triggered.connect(self.waypoint_table.slot_delete_all_waypoints)
        self.scan_for_devices_action.toggled.connect(self.slot_toggle_device_scan)

    def _init_log_dock(self):
        self.resizeDocks([self.log_dock], [150], Qt.Vertical)
        # Sync toggle action with log dock visibility
        self.toggle_debug_log_action.setChecked(self.log_dock.isVisible())

    @Slot()
    def slot_import_locations_fit(self) -> None:
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

            self.waypoint_table.waypoints = (
                self.waypoint_table.waypoints + fit_file_data_container.locations
            )

            self.logger.log(
                f"Successfully imported and appended from FIT file: {file_path}. Waypoints added: {len(fit_file_data_container.locations)}"
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
            self.waypoint_table.waypoints = self.waypoint_table.waypoints + waypoints

            self.logger.log(
                f"Successfully imported and appended from GPX file: {file_path}. Waypoints added: {len(waypoints)}"
            )

        except Exception as e:
            self.logger.error(f"Failed to import GPX file: {e}")
            QMessageBox.critical(self, "Import Error", f"Could not import GPX file: {e}")

    @Slot()
    def slot_save_locations_fit(self) -> None:
        from location_tool.save_fit_dialog import SaveFitDialog

        current_waypoints = self.waypoint_table.waypoints
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
            locations=current_waypoints,  # current_waypoints is List[WaypointData]
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

    # MTP Device Manager Slots

    @Slot(dict)
    def slot_device_found(self, device_info: dict) -> None:
        self.logger.log(f"Device found: {device_info['manufacturer']} {device_info['model']}")
        self.status_bar.showMessage(
            f"🟢 Device found: {device_info['manufacturer']} {device_info['model']}"
        )

    @Slot(str)
    def slot_device_error(self, error: str) -> None:
        self.logger.error(f"Device error: {error}")
        self.status_bar.showMessage("🔴 No MTP device found")

    @Slot(bool)
    def slot_toggle_device_scan(self, checked: bool) -> None:
        if checked:
            self.mtp_device_manager.start_scanning()
            self.logger.log("Device scanning started.")

        else:
            self.mtp_device_manager.stop_scanning()
            self.logger.log("Device scanning stopped.")

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
