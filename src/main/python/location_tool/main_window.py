import tempfile
from pathlib import Path
from typing import Any, List, Optional

from fit_tool.profile.profile_type import LocationSettings as FitLocationSettingsEnum
from PySide6.QtCore import QSize, Qt, Slot
from PySide6.QtGui import QAction, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
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
from .mode_select_dialog import ModeSelectDialog
from .ui.ui_main_window import Ui_MainWindow
from .utils import logger
from .utils.utils import colored_icon, get_resource_path
from .waypoints.table import WaypointTable


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, appctxt: Any, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.appctxt = appctxt
        self._init_logger()  # Initialize logger first

        # Initialize core application state and handlers
        self._init_internal_state()
        self._init_file_handlers()

        # Initialize UI elements and their specific configurations
        self._configure_ui_elements()

        # Initialize actions and connect signals
        self._setup_actions_and_connections()

        # Initialize MTP device management
        self._init_mtp_manager()

        # Set initial UI states that depend on actions or other setup
        self._set_initial_ui_states()

        self.logger.log("Application started.")

    def _init_logger(self):
        self.logger = logger.Logger.get_logger(self.log_textedit)

    def _init_internal_state(self):
        """Initializes core internal state variables."""
        self.device_connected: Optional[bool] = None
        self.loaded_location_settings: Optional[FitLocationSettingsEnum] = None
        self.current_file_path: Optional[str] = None

    def _init_file_handlers(self):
        """Initializes file handlers for FIT and GPX files."""
        self.fit_handler = FitFileHandler(self.appctxt)
        self.gpx_handler = GpxFileHandler(self.appctxt)

    def _configure_ui_elements(self):
        """Configures various UI elements like icons, tables, and docks."""
        self._init_icons()
        self._init_waypoint_table()
        self._configure_log_dock()

    def _init_icons(self):
        s = QSize(48, 48)
        self.import_file_action.setIcon(
            colored_icon(self.appctxt, "ui_icons/file_open.svg", s),
        )
        self.save_file_action.setIcon(
            colored_icon(self.appctxt, "ui_icons/save.svg", s),
        )

        self.toggle_debug_log_action.setIcon(colored_icon(self.appctxt, "ui_icons/terminal.svg", s))
        self.scan_for_devices_action.setIcon(
            colored_icon(self.appctxt, "ui_icons/devices_wearables.svg", s)
        )
        self.download_locations_fit_action.setIcon(
            colored_icon(self.appctxt, "ui_icons/mobile_arrow_down.svg", s)
        )
        self.upload_locations_fit_action.setIcon(
            colored_icon(self.appctxt, "ui_icons/mobile_arrow_up.svg", s)
        )

        self.add_wpt_btn.setIcon(colored_icon(self.appctxt, "ui_icons/add_2.svg", s))
        self.delete_wpt_btn.setIcon(colored_icon(self.appctxt, "ui_icons/remove_2.svg", s))
        self.add_wpt_action.setIcon(colored_icon(self.appctxt, "ui_icons/add_location.svg", s))
        self.delete_wpt_action.setIcon(
            colored_icon(self.appctxt, "ui_icons/remove_location.svg", s)
        )

    def _init_waypoint_table(self):
        """Initializes the waypoint table."""
        self.waypoint_table = WaypointTable(self.waypoint_table, self, self.appctxt)

    def _configure_log_dock(self):
        """Configures the properties of the log dock."""
        self.resizeDocks([self.log_dock], [150], Qt.Vertical)

    def _setup_actions_and_connections(self):
        """Sets up QActions, adds them to the window, and connects their signals."""
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

    def _init_mtp_manager(self):
        """Initializes the MTP device manager and connects its signals."""
        self.mtp_device_manager = MTPDeviceManager(self.appctxt, self)
        self.mtp_device_manager.device_found.connect(self.slot_device_found)
        self.mtp_device_manager.device_error.connect(self.slot_device_error)

    def _set_initial_ui_states(self):
        """Sets the initial states for various UI elements."""
        self.scan_for_devices_action.setChecked(True)
        self.log_dock.setVisible(False)
        self.toggle_debug_log_action.setChecked(self.log_dock.isVisible())

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

    def _set_status_icon_message(self, icon_path, message):
        # Remove previous status widget if exists
        if hasattr(self, "_status_widget") and self._status_widget:
            self.status_bar.removeWidget(self._status_widget)
        # Create a container widget
        status_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 0, 4)
        status_widget.setLayout(layout)
        # Icon
        icon_label = QLabel()
        pixmap = QPixmap(icon_path)
        icon_label.setPixmap(pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        # Text
        text_label = QLabel(message)
        text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # Add to layout
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addStretch()
        # Add to status bar
        self.status_bar.addWidget(status_widget)
        self._status_widget = status_widget
        self.status_bar.showMessage("")

    @Slot()
    def download_locations_fit(self) -> None:
        self.logger.log("Downloading locations from FIT file.")

        if self.device_connected is False:
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

        if self.device_connected is False:
            QMessageBox.critical(self, "No Device", "No MTP device connected.")
            return
        self.mtp_device_manager.stop_scanning()
        # Use a temporary file for the upload
        with tempfile.NamedTemporaryFile(delete=False, suffix=".fit") as temp_file:
            temp_file_path = Path(temp_file.name)
        self._save_locations_fit(self.waypoint_table.waypoints, str(temp_file_path))

        def on_done():
            QMessageBox.information(
                self,
                "Upload Successful",
                f"File {temp_file_path} uploaded successfully to {temp_file_path}",
            )
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

        self.mtp_device_manager.start_upload(
            str(temp_file_path), "Garmin/NewFiles/", on_done, on_error
        )

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
        mode_str = ModeSelectDialog.get_mode(self)
        if not mode_str:
            QMessageBox.warning(self, "No Mode", "Please select a save mode.")
            return
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
        if self.device_connected is True:
            return  # No change, already connected
        self.device_connected = True
        self.logger.log(f"Device found: {device_info['manufacturer']} {device_info['model']}")
        icon_path = get_resource_path(self.appctxt, "ui_icons/connected.png")
        msg = f"Device found: {device_info['manufacturer']} {device_info['model']}"
        self._set_status_icon_message(icon_path, msg)
        self.download_locations_fit_action.setEnabled(True)
        self.upload_locations_fit_action.setEnabled(True)

    @Slot(str)
    def slot_device_error(self, error: str) -> None:
        if self.device_connected is False:
            return  # No change, already disconnected
        self.device_connected = False
        self.logger.error(f"Device error: {error}")
        icon_path = get_resource_path(self.appctxt, "ui_icons/disconnected.png")
        msg = "No MTP device found"
        self._set_status_icon_message(icon_path, msg)
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
