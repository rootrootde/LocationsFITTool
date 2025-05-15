from PySide6.QtWidgets import QDialog, QFileDialog

from .ui_layouts.ui_save_fit_dialog import Ui_save_fit_dialog


class SaveFitDialog(QDialog, Ui_save_fit_dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.selected_save_path_le.setText("")
        self.mode_add_rb.setChecked(True)  # Default to ADD
        self.select_save_path_btn.clicked.connect(self.select_save_path)

    def select_save_path(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Locations FIT File", "Locations.fit", "FIT Files (*.fit)"
        )
        if file_path:
            if not file_path.lower().endswith(".fit"):
                file_path += ".fit"
            self.selected_save_path_le.setText(file_path)

    def get_save_path(self):
        return self.selected_save_path_le.text().strip()

    def get_mode(self):
        if self.mode_add_rb.isChecked():
            return "ADD"
        elif self.mode_replace_rb.isChecked():
            return "REPLACE"
        elif self.mode_delete_all_rb.isChecked():
            return "DELETE_ALL"
        return "ADD"  # Default
