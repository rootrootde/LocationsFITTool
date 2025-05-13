from typing import Optional

from fit_tool.profile.profile_type import LocationSettings as FitLocationSettingsEnum
from location_tool import files, fit_handler, logging_utils
from location_tool import settings as app_settings
from location_tool import table as table_manager
from location_tool import waypoints as waypoint_manager
from location_tool.ui_main_window import Ui_MainWindow
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QMainWindow,
    QMessageBox,
)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, appctxt, parent=None):
        super().__init__(parent)
        self.appctxt = appctxt
        self.setupUi(self)
        self.resizeDocks([self.log_dock], [100], Qt.Vertical)

        # Initialize logger
        self.logger = logging_utils.Logger(
            self.log_textedit, app_name="LocationsFITTool"
        )

        # add all actions to the main window to enable shortcuts
        for action in self.findChildren(QAction):
            self.addAction(action)

        self.current_waypoints_data: list[fit_handler.FitLocationData] = []
        self.loaded_location_settings: Optional[FitLocationSettingsEnum] = None
        self.current_file_path: Optional[str] = None
        self.fit_header_defaults: Optional[fit_handler.FitHeaderData] = None
        self.fit_creator_defaults: Optional[fit_handler.FitCreatorData] = None

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

        self._load_fit_header_defaults()
        self._load_fit_creator_defaults()

        self._setup_waypoints_table()
        self._clear_all_forms_and_tables()

    def _get_selected_table_rows(self) -> list[int]:
        """Gets a sorted list of unique selected row indices from the table, in descending order."""
        if not self.waypoint_table:
            return []

        selected_ranges = self.waypoint_table.selectedRanges()
        if not selected_ranges:
            return []

        rows_to_delete = set()
        for sr in selected_ranges:
            for r in range(sr.topRow(), sr.bottomRow() + 1):
                rows_to_delete.add(r)

        return sorted(list(rows_to_delete), reverse=True)

    def _load_fit_header_defaults(self):
        self.fit_header_defaults = app_settings.load_fit_header_defaults()
        if self.fit_header_defaults:
            self.logger.log(f"Loaded FIT header defaults: {self.fit_header_defaults}")
        else:
            self.logger.log("No FIT header defaults found or error loading them.")

    def _load_fit_creator_defaults(self):
        self.fit_creator_defaults = app_settings.load_fit_creator_defaults()
        if self.fit_creator_defaults:
            self.logger.log(f"Loaded FIT creator defaults: {self.fit_creator_defaults}")
        else:
            self.logger.log("No FIT creator defaults found or error loading them.")

    def _save_fit_header_defaults(self, header: Optional[fit_handler.FitHeaderData]):
        app_settings.save_fit_header_defaults(header)
        self.fit_header_defaults = header
        if header:
            self.logger.log(f"Saved FIT header defaults: {header}")
        else:
            self.logger.log("Cleared FIT header defaults.")

    def _save_fit_creator_defaults(self, creator: Optional[fit_handler.FitCreatorData]):
        app_settings.save_fit_creator_defaults(creator)
        self.fit_creator_defaults = creator
        if creator:
            self.logger.log(f"Saved FIT creator defaults: {creator}")
        else:
            self.logger.log("Cleared FIT creator defaults.")

    def _get_fit_header_for_save(self) -> Optional[fit_handler.FitHeaderData]:
        return self.fit_header_defaults

    def _get_fit_creator_for_save(self) -> Optional[fit_handler.FitCreatorData]:
        return self.fit_creator_defaults

    def _setup_waypoints_table(self):
        table_manager.setup_waypoints_table(self.waypoint_table, self)

    def _populate_waypoints_table(self):
        table_manager.populate_waypoints_table(
            self.waypoint_table,
            self.current_waypoints_data,
            self.appctxt,
            self.logger.log,
        )

    def _clear_all_forms_and_tables(self):
        self.current_waypoints_data = []
        self.loaded_location_settings = None
        if self.location_settings_combo.count() > 0:
            self.location_settings_combo.setCurrentIndex(0)
        self.waypoint_table.setRowCount(0)
        self.logger.clear_log()

    @Slot()
    def slot_import_locations_fit(self):
        file_path, fit_file_data_container = files.import_fit_file(
            self, logger=self.logger.log
        )
        if not file_path or not fit_file_data_container:
            self.logger.log("FIT file import cancelled or failed.")
            return

        self.current_file_path = file_path
        self.logger.log(f"Imported data from: {file_path}")

        if fit_file_data_container.header:
            self._save_fit_header_defaults(fit_file_data_container.header)
        if fit_file_data_container.creator:
            self._save_fit_creator_defaults(fit_file_data_container.creator)

        if fit_file_data_container.location_settings:
            # Access the stored LocationSettings enum from FitLocationSettingData
            self.loaded_location_settings = (
                fit_file_data_container.location_settings.location_settings_enum
            )
            if self.loaded_location_settings:
                for i in range(self.location_settings_combo.count()):
                    if (
                        self.location_settings_combo.itemData(i)
                        == self.loaded_location_settings
                    ):
                        self.location_settings_combo.setCurrentIndex(i)
                        break
                self.logger.log(
                    f"Loaded location settings: {self.loaded_location_settings.name}"
                )
            else:
                self.logger.log(
                    "No specific location settings enum found in FIT file's location_settings data."
                )
        else:
            self.logger.log("No location settings data block in FIT file.")

        self.current_waypoints_data = fit_file_data_container.locations
        self.current_waypoints_data = waypoint_manager.reindex_waypoints(
            self.current_waypoints_data
        )
        self._populate_waypoints_table()
        self.logger.log(
            f"Loaded {len(self.current_waypoints_data)} waypoints from FIT file."
        )
        if fit_file_data_container.errors:
            for error in fit_file_data_container.errors:
                self.logger.error(f"FIT Read Error: {error}")

    @Slot()
    def slot_import_gpx(self):
        file_path, gpx_waypoints = files.import_gpx_file(self, logger=self.logger.log)
        if not file_path or gpx_waypoints is None:
            self.logger.log("GPX file import cancelled or failed.")
            return

        self.current_file_path = file_path
        self.logger.log(f"Imported data from: {file_path}")

        self.current_waypoints_data = gpx_waypoints
        self.current_waypoints_data = waypoint_manager.reindex_waypoints(
            self.current_waypoints_data
        )
        self._populate_waypoints_table()
        self.logger.log(
            f"Loaded {len(self.current_waypoints_data)} waypoints from GPX file."
        )

    @Slot()
    def slot_save_locations_fit(self):
        if not self.current_waypoints_data:
            QMessageBox.information(
                self, "No Waypoints", "There are no waypoints to save."
            )
            self.logger.log("Save cancelled: No waypoints to save.")
            return

        save_file_path = self.current_file_path
        if not save_file_path or not save_file_path.endswith(".fit"):
            save_file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Locations.fit File", "", "FIT Files (*.fit)"
            )
            if not save_file_path:
                self.logger.log("Save cancelled by user.")
                return
            if not save_file_path.endswith(".fit"):
                save_file_path += ".fit"
            self.current_file_path = save_file_path

        fit_header_to_save = self._get_fit_header_for_save()
        if not fit_header_to_save:
            self.logger.warning(
                "FIT header defaults not found. Using application defaults for saving."
            )
            fit_header_to_save = fit_handler.FitHeaderData()
            self._save_fit_header_defaults(fit_header_to_save)

        fit_creator_to_save = self._get_fit_creator_for_save()
        if not fit_creator_to_save:
            self.logger.warning(
                "FIT creator defaults not found. Using application defaults for saving."
            )
            fit_creator_to_save = fit_handler.FitCreatorData()
            self._save_fit_creator_defaults(fit_creator_to_save)

        selected_location_setting_enum = self.location_settings_combo.currentData()
        fit_location_setting_data = None
        if isinstance(selected_location_setting_enum, FitLocationSettingsEnum):
            fit_location_setting_data = fit_handler.FitLocationSettingData(
                location_settings_enum=selected_location_setting_enum
            )
        else:
            self.logger.log(
                "No valid location setting selected, using default in FIT file."
            )

        fit_file_data_to_save = fit_handler.LocationsFitFileData(
            header=fit_header_to_save,
            creator=fit_creator_to_save,
            location_settings=fit_location_setting_data,
            locations=self.current_waypoints_data,
        )

        success, warnings, critical_errors = files.save_fit_file(
            self, save_file_path, fit_file_data_to_save, logger=self.logger.log
        )

        if success:
            self.logger.log(f"File successfully saved to {save_file_path}.")
        else:
            self.logger.error(f"Failed to save file to {save_file_path}.")

    @Slot()
    def slot_add_waypoint(self):
        self.current_waypoints_data, new_wp = waypoint_manager.add_waypoint(
            self.current_waypoints_data
        )
        if new_wp:
            self._populate_waypoints_table()
            self.logger.log(f"Added '{new_wp.name}'. Edit details in the table.")

            new_row_index = -1
            for i, wp_data in enumerate(self.current_waypoints_data):
                if wp_data.message_index == new_wp.message_index:
                    new_row_index = i
                    break

            if new_row_index != -1:
                self.waypoint_table.selectRow(new_row_index)
                self.waypoint_table.scrollToItem(
                    self.waypoint_table.item(new_row_index, 0),
                    QAbstractItemView.ScrollHint.EnsureVisible,
                )
                self.waypoint_table.editItem(self.waypoint_table.item(new_row_index, 0))
            else:
                row_count = self.waypoint_table.rowCount()
                if row_count > 0:
                    self.waypoint_table.selectRow(row_count - 1)
                    self.waypoint_table.scrollToItem(
                        self.waypoint_table.item(row_count - 1, 0),
                        QAbstractItemView.ScrollHint.EnsureVisible,
                    )
                    self.waypoint_table.editItem(
                        self.waypoint_table.item(row_count - 1, 0)
                    )

    @Slot()
    def slot_delete_selected_waypoint(self):
        selected_rows = self._get_selected_table_rows()
        if not selected_rows:
            QMessageBox.information(
                self, "No Selection", "Select waypoint(s) to delete."
            )
            return

        self.current_waypoints_data, num_deleted, new_selection_row = (
            waypoint_manager.delete_waypoints(
                self.current_waypoints_data, selected_rows
            )
        )

        self._populate_waypoints_table()

        if self.waypoint_table.rowCount() > 0:
            if (
                new_selection_row >= 0
                and new_selection_row < self.waypoint_table.rowCount()
            ):
                self.waypoint_table.selectRow(new_selection_row)
            elif self.waypoint_table.rowCount() > 0:
                self.waypoint_table.selectRow(0)

        if num_deleted > 0:
            self.logger.log(f"{num_deleted} waypoint(s) deleted.")

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
            self.current_waypoints_data = waypoint_manager.delete_all_waypoints()
            self._populate_waypoints_table()
            self.logger.log("All waypoints deleted.")
