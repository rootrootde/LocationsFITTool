# filepath: /Users/chris/Coding/LocationsFITTool/src/main/python/location_tool/files.py
from location_tool import fit_handler
from location_tool.fit_handler import (
    read_gpx_file,  # CHANGED: Import from fit_handler
)
from PySide6.QtWidgets import QFileDialog, QMessageBox


def import_fit_file(parent_widget, logger=print):
    file_path, _ = QFileDialog.getOpenFileName(
        parent_widget, "Import Locations.fit File", "", "FIT Files (*.fit)"
    )
    if not file_path:
        return None, None

    try:
        fit_file_data_container = fit_handler.read_fit_file(file_path)
        if fit_file_data_container.errors:
            for error in fit_file_data_container.errors:
                logger(f"FIT Read Error: {error}")
                QMessageBox.warning(parent_widget, "FIT Read Warning", str(error))
        return file_path, fit_file_data_container
    except Exception as e:
        logger(f"Failed to import FIT file: {e}")
        QMessageBox.critical(
            parent_widget, "Import Error", f"Could not import FIT file: {e}"
        )
        return None, None


def import_gpx_file(parent_widget, logger=print):
    file_path, _ = QFileDialog.getOpenFileName(
        parent_widget, "Import GPX File", "", "GPX Files (*.gpx)"
    )
    if not file_path:
        return None, None

    try:
        waypoints, errors = read_gpx_file(file_path, logger=logger)  # Pass logger
        if errors:
            for error in errors:
                logger(f"GPX Read Error/Warning: {error}")
                QMessageBox.warning(parent_widget, "GPX Read Warning", str(error))  # ADDED QMessageBox
        return file_path, waypoints  # ADDED return
    except Exception as e:
        logger(f"Failed to import GPX file: {e}")
        QMessageBox.critical(
            parent_widget, "Import Error", f"Could not import GPX file: {e}"
        )
        return None, None


def save_fit_file(
    parent_widget,
    file_path,
    fit_data_container: fit_handler.LocationsFitFileData,
    logger=print,
):
    try:
        success, warnings, critical_errors = fit_handler.write_fit_file(
            file_path, fit_data_container
        )
        if critical_errors:
            for error in critical_errors:
                logger(f"Critical FIT Save Error: {error}")
                QMessageBox.critical(parent_widget, "FIT Save Error", str(error))
            return False, warnings, critical_errors

        if warnings:
            for warning in warnings:
                logger(f"FIT Save Warning: {warning}")
                QMessageBox.warning(parent_widget, "FIT Save Warning", str(warning))

        if success:
            QMessageBox.information(
                parent_widget,
                "Save Successful",
                f"File saved successfully to {file_path}",
            )
        return success, warnings, critical_errors

    except Exception as e:
        logger(f"Failed to save FIT file: {e}")
        QMessageBox.critical(
            parent_widget, "Save Error", f"Could not save FIT file: {e}"
        )
        return False, [], [str(e)]
