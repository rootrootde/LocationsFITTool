import os
import tempfile
from pathlib import Path
from typing import Any, List, Optional

from fit_tool.profile.profile_type import FileType
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
from .geodata_model import GeoDataItem, GeoDataModel
from .gpx import GpxFileHandler
from .logger import Logger
from .mtp import MTPDeviceManager
from .theme import ThemeManager
from .ui.ui_main_window import Ui_MainWindow
from .utils import colored_icon
from .waypoints import WaypointTable


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(
        self, appctxt: Any, theme_manager: ThemeManager, parent: Optional[QWidget] = None
    ) -> None:
        """Initialize the main window."""
        super().__init__(parent)
        self.setupUi(self)

        self.appctxt = appctxt
        self.theme_manager = theme_manager
        self.logger = Logger.get_logger(self.log_textedit)

        self.current_file_path: Optional[str] = None

        self.fit_handler = FitFileHandler(self.appctxt)
        self.gpx_handler = GpxFileHandler(self.appctxt)

        self.mtp_device_manager = MTPDeviceManager(self.appctxt, self)

        self.waypoint_table = WaypointTable(self.appctxt, self.waypoint_table, self)
        self.resizeDocks([self.log_dock], [150], Qt.Vertical)

        self.geodata_model = GeoDataModel(self)
        self.geodata_view.setModel(self.geodata_model)

        self._setup_actions_and_connections()
        self._setup_icons()

        self.scan_for_devices_action.setChecked(True)
        self.log_dock.setVisible(False)
        self.toggle_debug_log_action.setChecked(self.log_dock.isVisible())

        self.logger.log("Application started.")

    def _setup_actions_and_connections(self) -> None:
        """Set up actions, signals, and shortcuts."""
        for action in self.findChildren(QAction):
            if isinstance(action, QAction):
                self.addAction(action)

        self.import_file_action.triggered.connect(self.slot_import_file)
        self.save_file_action.triggered.connect(self.slot_save_file)
        self.toggle_debug_log_action.toggled.connect(self.slot_toggle_log_dock)
        self.log_dock.visibilityChanged.connect(self.toggle_debug_log_action.setChecked)
        self.scan_for_devices_action.toggled.connect(self.slot_toggle_device_scan)
        self.download_locations_fit_action.triggered.connect(self.download_locations_fit)
        self.upload_locations_fit_action.triggered.connect(self.upload_locations_fit)

        self.mtp_device_manager.device_found.connect(self.slot_device_found)
        self.mtp_device_manager.device_error.connect(self.slot_device_error)

    def _setup_icons(self) -> None:
        """Set up themed icons for actions and buttons."""
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

    @Slot()
    def slot_import_file(self) -> None:
        """Open file dialog and import FIT or GPX file."""
        file_path, selected_filter = QFileDialog.getOpenFileName(
            self, "Import File", "", "FIT files (*.fit);;GPX files (*.gpx)"
        )
        if not file_path:
            return

        if selected_filter == "FIT files (*.fit)":
            fit_data = self.fit_handler.parse_fit_file(file_path)
            if fit_data:
                self.geodata_model.add_file_data(Path(file_path).name, fit_data, file_path)
                self.current_file_path = file_path
                self.update_window_title()
                self.logger.log(f"Successfully imported FIT file: {file_path}")
                self.tabWidget.setCurrentWidget(self.tab_geodata_explorer)
            else:
                QMessageBox.warning(self, "Import Error", f"Could not parse FIT file: {file_path}")
                self.logger.error(f"Could not parse FIT file: {file_path}")

        elif selected_filter == "GPX files (*.gpx)":
            self._import_gpx(file_path)
        else:
            QMessageBox.critical(self, "Import Error", "Unsupported file type.")

    def _import_locations_fit(self, file_path: str) -> None:
        """Import waypoints from a Locations.FIT file into the GeoDataView."""
        self.logger.log(f"Importing Locations.FIT: {file_path}")
        fit_file_data_container = self.fit_handler.parse_fit_file(file_path)

        if isinstance(fit_file_data_container, LocationsFitFileData):
            self.geodata_model.add_file_data(
                Path(file_path).name, fit_file_data_container, file_path
            )
            self.current_file_path = file_path
            self.logger.log(
                f"Imported {len(fit_file_data_container.locations)} waypoints from {Path(file_path).name}"
            )
            self.update_window_title()
            self.tabWidget.setCurrentWidget(self.tab_geodata_explorer)
        elif fit_file_data_container:
            QMessageBox.warning(
                self,
                "Import Error",
                f"File {Path(file_path).name} is not a valid Locations FIT file. Contained: {type(fit_file_data_container).__name__}",
            )
            self.logger.error(
                f"File {Path(file_path).name} is not a valid Locations FIT file. Contained: {type(fit_file_data_container).__name__}"
            )
        else:
            QMessageBox.warning(
                self, "Import Error", f"Could not parse FIT file: {Path(file_path).name}"
            )
            self.logger.error(f"Could not parse FIT file: {Path(file_path).name}")

    def _import_gpx(self, file_path: str) -> None:
        """Import data from a GPX file into the GeoDataView."""
        self.logger.log(f"Importing GPX: {file_path}")
        gpx_data = self.gpx_handler.parse_gpx_file(file_path)

        if gpx_data:
            self.geodata_model.add_file_data(Path(file_path).name, gpx_data, file_path)
            self.current_file_path = file_path
            count_str = []
            if gpx_data.waypoints:
                count_str.append(f"{len(gpx_data.waypoints)} waypoints")
            if gpx_data.tracks:
                count_str.append(f"{len(gpx_data.tracks)} tracks")
            if gpx_data.routes:
                count_str.append(f"{len(gpx_data.routes)} routes")
            self.logger.log(
                f"Imported {', '.join(count_str) if count_str else 'empty GPX'} from {Path(file_path).name}"
            )
            self.update_window_title()
            self.tabWidget.setCurrentWidget(self.tab_geodata_explorer)
        else:
            QMessageBox.warning(self, "Import Error", f"Could not parse GPX file: {file_path}")
            self.logger.error(f"Could not parse GPX file: {file_path}")

    @Slot()
    def slot_save_file(self) -> None:
        """Save the currently active data to a GPX or FIT file based on selection in GeoDataView."""
        if not self.geodata_model.hasChildren():
            QMessageBox.information(self, "Nothing to Save", "There is no data to save.")
            return

        first_file_item_index = self.geodata_model.index(0, 0)
        if not first_file_item_index.isValid():
            QMessageBox.information(self, "Nothing to Save", "No file loaded to save.")
            return

        file_node = self.geodata_model.itemFromIndex(first_file_item_index)
        if not isinstance(file_node, GeoDataItem) or not file_node.is_file_node():
            QMessageBox.information(self, "Save Error", "Selected item is not a file node.")
            return

        original_file_path = file_node.data_object().get("file_path", "")
        original_file_name = Path(original_file_path).name if original_file_path else "geodata"
        original_suffix = Path(original_file_path).suffix.lower() if original_file_path else ".gpx"

        dialog = QFileDialog(self, "Save File", str(Path.home()))
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setNameFilters(["GPX files (*.gpx)", "FIT files (*.fit)"])
        if original_suffix == ".fit":
            dialog.selectNameFilter("FIT files (*.fit)")
        else:
            dialog.selectNameFilter("GPX files (*.gpx)")
        dialog.setDefaultSuffix(original_suffix.lstrip("."))
        dialog.selectFile(original_file_name)

        if dialog.exec():
            save_file_path = dialog.selectedFiles()[0]
            selected_filter = dialog.selectedNameFilter()
            file_data_to_save = self.geodata_model.get_all_data_from_node(file_node)

            if selected_filter == "GPX files (*.gpx)":
                all_waypoints = file_data_to_save.get("waypoints", [])
                all_tracks = file_data_to_save.get("tracks", [])
                all_routes = file_data_to_save.get("routes", [])
                success = self.gpx_handler.write_gpx_file(
                    save_file_path, all_waypoints, all_tracks, all_routes
                )
                if success:
                    self.logger.log(f"Data saved to GPX: {save_file_path}")
                else:
                    QMessageBox.warning(
                        self, "Save Error", f"Could not save GPX to {save_file_path}"
                    )
                    self.logger.error(f"Could not save GPX to {save_file_path}")

            elif selected_filter == "FIT files (*.fit)":
                original_node_data = file_node.data_object()
                fit_file_type_hint = original_node_data.get("fit_type_hint", None)

                if file_data_to_save.get("waypoints") and (
                    not file_data_to_save.get("tracks")
                    and not file_data_to_save.get("routes")
                    or fit_file_type_hint == "LocationsFitFileData"
                ):
                    fit_data = LocationsFitFileData(
                        file_id=FileIdMessageData(file_type=FileType.LOCATIONS),
                        creator=FileCreatorMessageData(),
                        locations=self.geodata_model._convert_waypoints_to_location_messages(
                            file_data_to_save.get("waypoints", [])
                        ),
                    )
                    success, _ = self.fit_handler.write_fit_file(
                        save_file_path, fit_data, data_type_hint="locations"
                    )
                elif file_data_to_save.get("routes") and (
                    fit_file_type_hint == "CoursesFitFileData"
                    or not file_data_to_save.get("tracks")
                ):
                    fit_data = self.fit_handler.convert_route_to_courses_fit_data(
                        file_data_to_save.get("routes", []),
                        file_id_data=FileIdMessageData(file_type=FileType.COURSES),
                    )
                    success, _ = self.fit_handler.write_fit_file(
                        save_file_path, fit_data, data_type_hint="courses"
                    )
                elif file_data_to_save.get("tracks") and (
                    fit_file_type_hint == "ActivityFitFileData"
                ):
                    fit_data = self.fit_handler.convert_track_to_activity_fit_data(
                        file_data_to_save.get("tracks", []),
                        file_id_data=FileIdMessageData(file_type=FileType.ACTIVITY),
                    )
                    success, _ = self.fit_handler.write_fit_file(
                        save_file_path, fit_data, data_type_hint="activity"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Save Error",
                        "Could not determine FIT file type to save. Data is mixed or empty.",
                    )
                    self.logger.error("Could not determine FIT file type for saving.")
                    return

                if success:
                    self.logger.log(f"Data saved to FIT: {save_file_path}")
                else:
                    QMessageBox.warning(
                        self, "Save Error", f"Could not save FIT to {save_file_path}"
                    )
                    self.logger.error(f"Could not save FIT to {save_file_path}")

    @Slot(str)
    def _save_locations_fit(self, current_waypoints: List[Any], file_path: str) -> Optional[bool]:
        """Save current waypoints to a Locations.FIT file."""
        self.logger.log(f"Saving {len(current_waypoints)} waypoints to Locations.FIT: {file_path}")
        if not current_waypoints:
            self.logger.warning("No waypoints to save.")
            return False

        file_id_data = FileIdMessageData(
            file_type=FileType.LOCATIONS,
            manufacturer=self.fit_handler.appctxt.build_settings.get("fit_manufacturer", 1),
            product=self.fit_handler.appctxt.build_settings.get("fit_product_id", 0),
            serial_number=12345,
            product_name=self.fit_handler.appctxt.app.applicationName(),
        )

        creator_data = FileCreatorMessageData(
            software_version=100,
            hardware_version=1,
        )

        location_settings_data = LocationSettingsMessageData(
            location_settings_enum=FitLocationSettingsEnum.WAYPOINTS_ENABLED
        )

        location_messages = [
            self.geodata_model._convert_waypoint_to_location_message(wp) for wp in current_waypoints
        ]

        fit_file_data = LocationsFitFileData(
            file_id=file_id_data,
            creator=creator_data,
            location_settings=location_settings_data,
            locations=location_messages,
        )

        success, errors = self.fit_handler.write_fit_file(
            file_path, fit_file_data, data_type_hint="locations"
        )
        if success:
            self.logger.log(f"Successfully saved Locations.FIT to {file_path}")
            return True
        else:
            self.logger.error(f"Error saving Locations.FIT: {errors}")
            QMessageBox.critical(self, "Save Error", f"Could not save Locations.FIT: {errors}")
            return False

    def _save_gpx(self, current_waypoints: List[Any], file_path: str) -> Optional[bool]:
        """Save current waypoints to a GPX file."""
        self.logger.log(f"Saving {len(current_waypoints)} waypoints to GPX: {file_path}")
        if not current_waypoints:
            self.logger.warning("No waypoints to save.")
            return False

        success = self.gpx_handler.write_gpx_file(
            file_path, waypoints=current_waypoints, tracks=[], routes=[]
        )
        if success:
            self.logger.log(f"Successfully saved GPX to {file_path}")
            return True
        else:
            self.logger.error(f"Error saving GPX: {file_path}")
            QMessageBox.critical(self, "Save Error", f"Could not save GPX: {file_path}")
            return False

    @Slot(dict)
    def download_locations_fit(self) -> None:
        """Download Locations.fit from the selected device and import it into the GeoDataView."""
        selected_device_info = self.mtp_device_manager.get_selected_device()
        if not selected_device_info:
            QMessageBox.warning(self, "Device Error", "No MTP device selected.")
            return

        with tempfile.NamedTemporaryFile(suffix=".fit", delete=False) as tmp_file:
            temp_file_path = tmp_file.name

        self.logger.log(f"Attempting to download Locations.fit to {temp_file_path}")

        success = self.mtp_device_manager.download_file_from_device(
            selected_device_info["path"],
            "Garmin/Locations/Locations.fit",
            temp_file_path,
        )

        if success:
            self.logger.log(f"Successfully downloaded Locations.fit to {temp_file_path}")
            fit_file_data_container = self.fit_handler.parse_fit_file(temp_file_path)
            if isinstance(fit_file_data_container, LocationsFitFileData):
                self.geodata_model.add_file_data(
                    "Locations.fit", fit_file_data_container, temp_file_path
                )
                self.current_file_path = temp_file_path
                self.logger.log(
                    f"Imported {len(fit_file_data_container.locations)} waypoints from downloaded Locations.fit"
                )
                self.update_window_title("Locations.fit (Device)")
                self.tabWidget.setCurrentWidget(self.tab_geodata_explorer)
            else:
                QMessageBox.warning(
                    self,
                    "Import Error",
                    "Downloaded Locations.fit is not a valid Locations FIT file or is empty.",
                )
                self.logger.error(
                    "Downloaded Locations.fit is not a valid Locations FIT file or is empty."
                )
        else:
            QMessageBox.critical(
                self, "Download Error", "Failed to download Locations.fit from device."
            )
            self.logger.error("Failed to download Locations.fit from device.")
            Path(temp_file_path).unlink(missing_ok=True)

    @Slot()
    def upload_locations_fit(self) -> None:
        """Upload waypoints from the 'Locations.fit' node in GeoDataView to the device."""
        selected_device_info = self.mtp_device_manager.get_selected_device()
        if not selected_device_info:
            QMessageBox.warning(self, "Device Error", "No MTP device selected.")
            return

        locations_node = self.geodata_model._get_or_create_locations_fit_node()
        if not locations_node or not locations_node.hasChildren():
            QMessageBox.information(
                self, "Upload Error", "No waypoints found in the 'Locations.fit' data to upload."
            )
            self.logger.warning("No 'Locations.fit' data to upload.")
            return

        waypoints_to_upload = self.geodata_model.get_all_waypoints_from_locations_node()
        if not waypoints_to_upload:
            QMessageBox.information(
                self, "Upload Error", "No waypoints found in the 'Locations.fit' data to upload."
            )
            self.logger.warning("No waypoints in 'Locations.fit' node to upload.")
            return

        with tempfile.NamedTemporaryFile(suffix=".fit", delete=False) as tmp_file:
            temp_fit_path = tmp_file.name

        self.logger.log(f"Preparing temporary Locations.fit for upload at: {temp_fit_path}")

        save_success = self._save_locations_fit(waypoints_to_upload, temp_fit_path)

        if not save_success:
            QMessageBox.critical(
                self, "Upload Error", "Failed to create temporary Locations.fit for upload."
            )
            self.logger.error("Failed to create temporary Locations.fit for upload.")
            Path(temp_fit_path).unlink(missing_ok=True)
            return

        self.logger.log(f"Attempting to upload {temp_fit_path} to device.")
        upload_success = self.mtp_device_manager.upload_file_to_device(
            selected_device_info["path"], temp_fit_path, "Garmin/NewFiles/Locations.fit"
        )

        if upload_success:
            self.logger.log("Successfully uploaded Locations.fit to device's NewFiles directory.")
            QMessageBox.information(
                self,
                "Upload Successful",
                "Locations.fit uploaded to device. The device will process it shortly.",
            )
        else:
            QMessageBox.critical(self, "Upload Error", "Failed to upload Locations.fit to device.")
            self.logger.error("Failed to upload Locations.fit to device.")

        Path(temp_fit_path).unlink(missing_ok=True)

    @Slot(bool)
    def slot_toggle_device_scan(self, checked: bool) -> None:
        """Toggle device scanning."""
        if checked:
            self.mtp_device_manager.start_scanning()
            self.logger.log("Device scanning started.")

        else:
            self.mtp_device_manager.stop_scanning()
            self.logger.log("Device scanning stopped.")

    @Slot(bool)
    def slot_toggle_log_dock(self, checked: bool) -> None:
        """Toggle log dock visibility."""
        if checked:
            self.log_dock.show()
        else:
            self.log_dock.hide()
        self.logger.log(f"Log window {'shown' if checked else 'hidden'}.")

    @Slot(dict)
    def slot_device_found(self, device_info: dict) -> None:
        """Handle device found event."""
        if self.mtp_device_manager.device_connected is True:
            return
        self.mtp_device_manager.device_connected = True
        self.logger.log(f"Device found: {device_info['manufacturer']} {device_info['model']}")
        msg = f"Device found: {device_info['manufacturer']} {device_info['model']}"
        self.status_bar.showMessage(msg)
        self.download_locations_fit_action.setEnabled(True)
        self.upload_locations_fit_action.setEnabled(True)

    @Slot(str)
    def slot_device_error(self, error: str) -> None:
        """Handle device error event."""
        if self.mtp_device_manager.device_connected is False:
            return
        self.mtp_device_manager.device_connected = False
        self.logger.error(f"Device error: {error}")
        msg = "No MTP device found"
        self.status_bar.showMessage(msg)
        self.download_locations_fit_action.setEnabled(False)
        self.upload_locations_fit_action.setEnabled(False)

    def update_window_title(self) -> None:
        """Updates the main window title based on the current file."""
        if self.model.gpx_file_path:
            title = f"{os.path.basename(self.model.gpx_file_path)} - GPX Editor"
        else:
            title = "GPX Editor"
        self.setWindowTitle(title)

    def closeEvent(self, event: Any) -> None:
        """Handle window close event."""
        self.logger.log("Application closing.")
        super().closeEvent(event)
