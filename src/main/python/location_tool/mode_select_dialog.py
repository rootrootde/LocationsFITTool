from PySide6.QtWidgets import QDialog

from .ui.ui_mode_select import Ui_mode_select_dialog
from .utils import colored_icon


class ModeSelectDialog(QDialog, Ui_mode_select_dialog):
    def __init__(self, appctxt, parent=None):
        """Initialize the mode select dialog."""
        super().__init__(parent)
        self.setupUi(self)
        self.appctxt = appctxt
        self._result = None
        self.mode_add_btn.clicked.connect(lambda: self._select("ADD"))
        self.mode_replace_btn.clicked.connect(lambda: self._select("REPLACE"))
        self.mode_delete_all_btn.clicked.connect(lambda: self._select("DELETE_ALL"))

    def _select(self, value):
        """Set the selected mode and accept the dialog."""
        self._result = value
        self.accept()

    @staticmethod
    def get_mode(appctxt, parent=None):
        """Show the dialog and return the selected mode."""
        dialog = ModeSelectDialog(appctxt, parent)
        if dialog.exec() == QDialog.Accepted:
            return dialog._result
        return None
