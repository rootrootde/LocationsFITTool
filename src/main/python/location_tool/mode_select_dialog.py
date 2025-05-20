from PySide6.QtWidgets import QDialog

from .ui.ui_mode_select import Ui_mode_select_dialog


class ModeSelectDialog(QDialog, Ui_mode_select_dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.mode_add_btn.setIcon(self.colored_icon("icons/add.svg", 32, "green"))
        self.mode_replace_btn.setIcon(self.colored_icon("icons/replace.svg", 32, "blue"))
        self.mode_delete_all_btn.setIcon(self.colored_icon("icons/delete.svg", 32, "red"))
        self._result = None

        self.mode_add_btn.clicked.connect(lambda: self._select("ADD"))
        self.mode_replace_btn.clicked.connect(lambda: self._select("REPLACE"))
        self.mode_delete_all_btn.clicked.connect(lambda: self._select("DELETE_ALL"))

    def _select(self, value):
        self._result = value
        self.accept()

    @staticmethod
    def get_mode(parent=None):
        dialog = ModeSelectDialog(parent)
        if dialog.exec() == QDialog.Accepted:
            return dialog._result
        return None
