import tempfile
from pathlib import Path
from typing import Any, List, Optional

from fit_tool.profile.profile_type import LocationSettings as FitLocationSettingsEnum
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QWidget

from .fit import FitFileHandler
from .fit_data import (
    FileCreatorMessageData,
    FileIdMessageData,
    LocationSettingsMessageData,
    LocationsFitFileData,
)
from .gpx import GpxFileHandler
from .logger import Logger
from .mode_select_dialog import ModeSelectDialog
from .mtp import MTPDeviceManager
from .theme import ThemeManager
from .ui.ui_main_window import Ui_MainWindow
from .utils import colored_icon
from .waypoints import WaypointTable


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(
        self, appctxt: Any, theme_manager: ThemeManager, parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.appctxt = appctxt
        self.theme_manager = theme_manager
        self.logger = Logger.get_logger(self.log_textedit)

        # Initialize core application state and handlers
        self.current_file_path: Optional[str] = None

        # Initialize file handlers
        self.fit_handler = FitFileHandler(self.appctxt)
        self.gpx_handler = GpxFileHandler(self.appctxt)

        # Initialize MTP device management
        self.mtp_device_manager = MTPDeviceManager(self.appctxt, self)

        # Initialize UI elements and their specific configurations
        self.waypoint_table = WaypointTable(self.appctxt, self.waypoint_table, self)
        self.resizeDocks([self.log_dock], [150], Qt.Vertical)

        # Initialize actions and connect signals
        self._setup_actions_and_connections()

        # Setup icons for actions
        self._setup_icons()

        # Set initial UI states that depend on actions or other setup
        self.scan_for_devices_action.setChecked(True)
        self.log_dock.setVisible(False)
        self.toggle_debug_log_action.setChecked(self.log_dock.isVisible())

        self.logger.log("Application started.")

    def _setup_actions_and_connections(self):
        """Setup actions and connections with themed icons."""

        # Add all actions to the main window to enable shortcuts
        for action in self.findChildren(QAction):
            if isinstance(action, QAction):
                self.addAction(action)

        # Connect actions to slots
        self.import_file_action.triggered.connect(self.slot_import_file)
        self.save_file_action.triggered.connect(self.slot_save_file)
        self.add_wpt_action.triggered.connect(self.waypoint_table.slot_add_waypoint)
        self.delete_wpt_action.triggered.connect(self.waypoint_table.slot_delete_selected_waypoints)
        self.toggle_debug_log_action.toggled.connect(self.slot_toggle_log_dock)
        self.log_dock.visibilityChanged.connect(self.toggle_debug_log_action.setChecked)
        self.scan_for_devices_action.toggled.connect(self.slot_toggle_device_scan)
        self.download_locations_fit_action.triggered.connect(self.download_locations_fit)
        self.upload_locations_fit_action.triggered.connect(self.upload_locations_fit)

        self.add_wpt_btn.clicked.connect(self.add_wpt_action.trigger)
        self.delete_wpt_btn.clicked.connect(self.delete_wpt_action.trigger)

        self.mtp_device_manager.device_found.connect(self.slot_device_found)
        self.mtp_device_manager.device_error.connect(self.slot_device_error)

    def _setup_icons(self):
        # Get the primary color for icons from theme manager
        c = self.theme_manager.primary_color
        s = (64, 64)

        self.logger.log(f"Primary color for icons: {c}")

        download_icon = colored_icon(self.appctxt, "ui_icons/download.svg", s, c)
        self.download_locations_fit_action.setIcon(download_icon)

        upload_icon = colored_icon(self.appctxt, "ui_icons/upload.svg", s, c)
        self.upload_locations_fit_action.setIcon(upload_icon)

        import_icon = colored_icon(self.appctxt, "ui_icons/import_locations.svg", s, c)
        self.import_file_action.setIcon(import_icon)

        save_icon = colored_icon(self.appctxt, "ui_icons/save_file.svg", s, c)
        self.save_file_action.setIcon(save_icon)

        add_icon = colored_icon(self.appctxt, "ui_icons/plus.svg", s, c)
        self.add_wpt_btn.setIcon(add_icon)

        delete_icon = colored_icon(self.appctxt, "ui_icons/minus.svg", s, c)
        self.delete_wpt_btn.setIcon(delete_icon)

    @Slot()
    def slot_import_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import File", "", "FIT Files (*.fit);;GPX Files (*.gpx)"
        )
        if not file_path:
            return

        if file_path.endswith(".fit"):
            self.current_file_path = file_path
            self._import_locations_fit(file_path)

        elif file_path.endswith(".gpx"):
            self.current_file_path = file_path
            self._import_gpx(file_path)
        else:
            QMessageBox.critical(self, "Import Error", "Unsupported file type.")

    def _import_locations_fit(self, file_path) -> None:
        try:
            fit_file_data_container = self.fit_handler.parse_fit_file(
                file_path, logger=self.logger.log
            )
            if fit_file_data_container.errors:
                for error in fit_file_data_container.errors:
                    self.logger.warning(f"FIT Read Warning: {error}")
                    QMessageBox.warning(self, "FIT Read Warning", str(error))

            self.waypoint_table.waypoints = (
                self.waypoint_table.waypoints + fit_file_data_container.locations
            )

            self.logger.log(
                f"Successfully imported and appended from FIT file: {file_path}. Waypoints added: {len(fit_file_data_container.locations)}"
            )
        except Exception as e:
            self.logger.error(f"Failed to import FIT file: {e}")
            QMessageBox.critical(self, "Import Error", f"Could not import FIT file: {e}")

    def _import_gpx(self, file_path) -> None:
        try:
            waypoints, errors = self.gpx_handler.parse_gpx_file(file_path)
            if errors:
                for error in errors:
                    self.logger.warning(f"GPX Read Error/Warning: {error}")
                    QMessageBox.warning(self, "GPX Read Warning", str(error))

            self.waypoint_table.waypoints = self.waypoint_table.waypoints + waypoints

            self.logger.log(
                f"Successfully imported and appended from GPX file: {file_path}. Waypoints added: {len(waypoints)}"
            )

        except Exception as e:
            self.logger.error(f"Failed to import GPX file: {e}")
            QMessageBox.critical(self, "Import Error", f"Could not import GPX file: {e}")

    @Slot()
    def download_locations_fit(self) -> None:
        self.logger.log("Downloading locations from FIT file.")

        if self.mtp_device_manager.device_connected is False:
            QMessageBox.critical(self, "No Device", "No MTP device connected.")
            return
        # Temporarily stop scanning
        self.mtp_device_manager.stop_scanning()
        # Use a temporary directory for the download
        temp_dir = tempfile.TemporaryDirectory()
        target_path = Path(temp_dir.name)
        fit_filename = "Locations.fit"
        fit_file_path = target_path / fit_filename

        def on_done():
            self.logger.log("Download finished. Importing Locations.fit...")
            self._import_locations_fit(str(fit_file_path))
            self.mtp_device_manager.start_scanning()
            temp_dir.cleanup()

        def on_error(err):
            self.logger.error(f"Download failed: {err}")
            self.mtp_device_manager.start_scanning()
            temp_dir.cleanup()

        self.mtp_device_manager.start_download(
            "Garmin/Locations/Locations.fit", str(target_path), on_done, on_error
        )

    @Slot()
    def upload_locations_fit(self) -> None:
        self.logger.log("Uploading locations to FIT file.")

        # Set the target path for the upload
        target_path = "Garmin/NewFiles/"

        if self.mtp_device_manager.device_connected is False:
            QMessageBox.critical(self, "No Device", "No MTP device connected.")
            return
        self.mtp_device_manager.stop_scanning()
        # Use a temporary file for the upload
        with tempfile.NamedTemporaryFile(delete=False, suffix=".fit") as temp_file:
            temp_file_path = Path(temp_file.name)
        success = self._save_locations_fit(self.waypoint_table.waypoints, str(temp_file_path))
        if not success:
            return

        def on_done():
            QMessageBox.information(self, "Upload Successful", "Please disconnect device now.")
            self.logger.log(f"File {temp_file_path} uploaded successfully to {target_path}")
            self.mtp_device_manager.start_scanning()
            try:
                temp_file_path.unlink()
            except Exception as e:
                self.logger.warning(f"Could not remove temp file: {e}")

        def on_error(err):
            self.logger.error(f"Upload failed: {err}")
            self.mtp_device_manager.start_scanning()
            try:
                temp_file_path.unlink()
            except Exception as e:
                self.logger.warning(f"Could not remove temp file: {e}")

        self.mtp_device_manager.start_upload(str(temp_file_path), target_path, on_done, on_error)

    @Slot(str)
    def slot_save_file(self) -> None:
        current_waypoints = self.waypoint_table.waypoints
        if not current_waypoints:
            QMessageBox.information(self, "No Data", "There are no waypoints to save.")
            return

        # Allow user to choose either .fit or .gpx file
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "Save Locations File", "", "FIT Files (*.fit);;GPX Files (*.gpx)"
        )
        if not file_path:
            QMessageBox.warning(self, "No Path", "Please select a save path.")
            return

        # Determine file type based on extension or selected filter
        if file_path.endswith(".fit") or "FIT" in selected_filter:
            self._save_locations_fit(current_waypoints, file_path)
        elif file_path.endswith(".gpx") or "GPX" in selected_filter:
            self._save_gpx(current_waypoints, file_path)
        else:
            QMessageBox.warning(self, "Unsupported File Type", "Please select a valid file type.")

    def _save_locations_fit(self, current_waypoints, file_path) -> None:
        mode_str = ModeSelectDialog.get_mode(self.appctxt, parent=self)
        if not mode_str:
            QMessageBox.warning(self, "No Mode", "Please select a save mode.")
            return False
        else:
            mode_enum = FitLocationSettingsEnum[mode_str]

        fit_data_container = LocationsFitFileData(
            file_id=FileIdMessageData(),
            creator=FileCreatorMessageData(),
            location_settings=LocationSettingsMessageData(location_settings_enum=mode_enum),
            locations=current_waypoints,
        )

        try:
            success: bool
            errors: List[str]

            success, errors = self.fit_handler.write_fit_file(file_path, fit_data_container)

            if errors:
                for error in errors:
                    self.logger.error(f"Critical FIT Save Error: {error}")
                    QMessageBox.critical(self, "FIT Save Error", str(error))
                return False

            return success

        except Exception as e:
            self.logger.error(f"Failed to save FIT file: {e}")
            QMessageBox.critical(self, "Save Error", f"Could not save FIT file: {e}")

    def _save_gpx(self, current_waypoints, file_path) -> None:
        file_path, _ = QFileDialog.getSaveFileName(self, "Save GPX File", "", "GPX Files (*.gpx)")
        if not file_path:
            QMessageBox.warning(self, "No Path", "Please select a save path.")
            return

        try:
            success: bool
            errors: List[str]

            success, errors = self.gpx_handler.write_gpx_file(file_path, current_waypoints)

            if errors:
                for error in errors:
                    self.logger.error(f"Critical GPX Save Error: {error}")
                    QMessageBox.critical(self, "GPX Save Error", str(error))
                return False

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
            self.logger.error(f"Failed to save GPX file: {e}")
            QMessageBox.critical(self, "Save Error", f"Could not save GPX file: {e}")

    @Slot(dict)
    def slot_device_found(self, device_info: dict) -> None:
        if self.mtp_device_manager.device_connected is True:
            return  # No change, already connected
        self.mtp_device_manager.device_connected = True
        self.logger.log(f"Device found: {device_info['manufacturer']} {device_info['model']}")
        msg = f"Device found: {device_info['manufacturer']} {device_info['model']}"
        self.status_bar.showMessage(msg)
        self.download_locations_fit_action.setEnabled(True)
        self.upload_locations_fit_action.setEnabled(True)

    @Slot(str)
    def slot_device_error(self, error: str) -> None:
        if self.mtp_device_manager.device_connected is False:
            return  # No change, already disconnected
        self.mtp_device_manager.device_connected = False
        self.logger.error(f"Device error: {error}")
        msg = "No MTP device found"
        self.status_bar.showMessage(msg)
        self.download_locations_fit_action.setEnabled(False)
        self.upload_locations_fit_action.setEnabled(False)

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
