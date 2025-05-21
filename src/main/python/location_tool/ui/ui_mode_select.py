# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mode_select.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QLabel,
    QLayout, QPushButton, QSizePolicy, QWidget)
from . import resources_rc

class Ui_mode_select_dialog(object):
    def setupUi(self, mode_select_dialog):
        if not mode_select_dialog.objectName():
            mode_select_dialog.setObjectName(u"mode_select_dialog")
        mode_select_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        mode_select_dialog.resize(565, 265)
        mode_select_dialog.setStyleSheet(u"")
        self.gridLayout = QGridLayout(mode_select_dialog)
        self.gridLayout.setSpacing(30)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.gridLayout.setContentsMargins(30, 30, 30, 30)
        self.mode_delete_all_lbl = QLabel(mode_select_dialog)
        self.mode_delete_all_lbl.setObjectName(u"mode_delete_all_lbl")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.mode_delete_all_lbl.sizePolicy().hasHeightForWidth())
        self.mode_delete_all_lbl.setSizePolicy(sizePolicy)
        self.mode_delete_all_lbl.setAlignment(Qt.AlignmentFlag.AlignJustify|Qt.AlignmentFlag.AlignTop)
        self.mode_delete_all_lbl.setWordWrap(True)

        self.gridLayout.addWidget(self.mode_delete_all_lbl, 1, 2, 1, 1)

        self.mode_replace_lbl = QLabel(mode_select_dialog)
        self.mode_replace_lbl.setObjectName(u"mode_replace_lbl")
        sizePolicy.setHeightForWidth(self.mode_replace_lbl.sizePolicy().hasHeightForWidth())
        self.mode_replace_lbl.setSizePolicy(sizePolicy)
        self.mode_replace_lbl.setAlignment(Qt.AlignmentFlag.AlignJustify|Qt.AlignmentFlag.AlignTop)
        self.mode_replace_lbl.setWordWrap(True)

        self.gridLayout.addWidget(self.mode_replace_lbl, 1, 1, 1, 1)

        self.mode_add_lbl = QLabel(mode_select_dialog)
        self.mode_add_lbl.setObjectName(u"mode_add_lbl")
        sizePolicy.setHeightForWidth(self.mode_add_lbl.sizePolicy().hasHeightForWidth())
        self.mode_add_lbl.setSizePolicy(sizePolicy)
        self.mode_add_lbl.setAlignment(Qt.AlignmentFlag.AlignJustify|Qt.AlignmentFlag.AlignTop)
        self.mode_add_lbl.setWordWrap(True)

        self.gridLayout.addWidget(self.mode_add_lbl, 1, 0, 1, 1)

        self.mode_add_btn = QPushButton(mode_select_dialog)
        self.mode_add_btn.setObjectName(u"mode_add_btn")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(1)
        sizePolicy1.setHeightForWidth(self.mode_add_btn.sizePolicy().hasHeightForWidth())
        self.mode_add_btn.setSizePolicy(sizePolicy1)
        self.mode_add_btn.setIconSize(QSize(64, 64))

        self.gridLayout.addWidget(self.mode_add_btn, 0, 0, 1, 1)

        self.mode_replace_btn = QPushButton(mode_select_dialog)
        self.mode_replace_btn.setObjectName(u"mode_replace_btn")
        sizePolicy1.setHeightForWidth(self.mode_replace_btn.sizePolicy().hasHeightForWidth())
        self.mode_replace_btn.setSizePolicy(sizePolicy1)
        self.mode_replace_btn.setIconSize(QSize(64, 64))

        self.gridLayout.addWidget(self.mode_replace_btn, 0, 1, 1, 1)

        self.mode_delete_all_btn = QPushButton(mode_select_dialog)
        self.mode_delete_all_btn.setObjectName(u"mode_delete_all_btn")
        sizePolicy1.setHeightForWidth(self.mode_delete_all_btn.sizePolicy().hasHeightForWidth())
        self.mode_delete_all_btn.setSizePolicy(sizePolicy1)
        self.mode_delete_all_btn.setIconSize(QSize(64, 64))

        self.gridLayout.addWidget(self.mode_delete_all_btn, 0, 2, 1, 1)


        self.retranslateUi(mode_select_dialog)

        QMetaObject.connectSlotsByName(mode_select_dialog)
    # setupUi

    def retranslateUi(self, mode_select_dialog):
        mode_select_dialog.setWindowTitle(QCoreApplication.translate("mode_select_dialog", u"Dialog", None))
        self.mode_delete_all_lbl.setText(QCoreApplication.translate("mode_select_dialog", u"Delete all waypoints on device.", None))
        self.mode_replace_lbl.setText(QCoreApplication.translate("mode_select_dialog", u"Delete all Waypoints on device and replace them with the new waypoints.", None))
        self.mode_add_lbl.setText(QCoreApplication.translate("mode_select_dialog", u"Add new waypoints to the existing ones on the device.", None))
        self.mode_add_btn.setText(QCoreApplication.translate("mode_select_dialog", u"Add", None))
        self.mode_replace_btn.setText(QCoreApplication.translate("mode_select_dialog", u"Replace", None))
        self.mode_delete_all_btn.setText(QCoreApplication.translate("mode_select_dialog", u"Delete All", None))
    # retranslateUi

