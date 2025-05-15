# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'save_fit_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QRadioButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_save_fit_dialog(object):
    def setupUi(self, save_fit_dialog):
        if not save_fit_dialog.objectName():
            save_fit_dialog.setObjectName(u"save_fit_dialog")
        save_fit_dialog.resize(557, 208)
        self.verticalLayout_2 = QVBoxLayout(save_fit_dialog)
#ifndef Q_OS_MAC
        self.verticalLayout_2.setSpacing(-1)
#endif
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(save_fit_dialog)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.selected_save_path_le = QLineEdit(save_fit_dialog)
        self.selected_save_path_le.setObjectName(u"selected_save_path_le")

        self.horizontalLayout.addWidget(self.selected_save_path_le)

        self.select_save_path_btn = QPushButton(save_fit_dialog)
        self.select_save_path_btn.setObjectName(u"select_save_path_btn")

        self.horizontalLayout.addWidget(self.select_save_path_btn)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.mode_group_box = QGroupBox(save_fit_dialog)
        self.mode_group_box.setObjectName(u"mode_group_box")
        self.mode_group_box.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.mode_group_box.setChecked(False)
        self.layout_2 = QVBoxLayout(self.mode_group_box)
        self.layout_2.setObjectName(u"layout_2")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignJustify|Qt.AlignmentFlag.AlignVCenter)
        self.formLayout.setFormAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.mode_add_rb = QRadioButton(self.mode_group_box)
        self.mode_add_rb.setObjectName(u"mode_add_rb")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.mode_add_rb)

        self.mode_add_lbl = QLabel(self.mode_group_box)
        self.mode_add_lbl.setObjectName(u"mode_add_lbl")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.mode_add_lbl)

        self.mode_replace_rb = QRadioButton(self.mode_group_box)
        self.mode_replace_rb.setObjectName(u"mode_replace_rb")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.mode_replace_rb)

        self.mode_replace_lbl = QLabel(self.mode_group_box)
        self.mode_replace_lbl.setObjectName(u"mode_replace_lbl")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.mode_replace_lbl)

        self.mode_delete_all_rb = QRadioButton(self.mode_group_box)
        self.mode_delete_all_rb.setObjectName(u"mode_delete_all_rb")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.mode_delete_all_rb)

        self.mode_delete_all_lbl = QLabel(self.mode_group_box)
        self.mode_delete_all_lbl.setObjectName(u"mode_delete_all_lbl")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.mode_delete_all_lbl)


        self.layout_2.addLayout(self.formLayout)


        self.verticalLayout_2.addWidget(self.mode_group_box)

        self.buttonBox = QDialogButtonBox(save_fit_dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Save)

        self.verticalLayout_2.addWidget(self.buttonBox)


        self.retranslateUi(save_fit_dialog)
        self.buttonBox.accepted.connect(save_fit_dialog.accept)
        self.buttonBox.rejected.connect(save_fit_dialog.reject)

        QMetaObject.connectSlotsByName(save_fit_dialog)
    # setupUi

    def retranslateUi(self, save_fit_dialog):
        save_fit_dialog.setWindowTitle(QCoreApplication.translate("save_fit_dialog", u"Save Locations.fit", None))
        self.label.setText(QCoreApplication.translate("save_fit_dialog", u"Path:", None))
        self.select_save_path_btn.setText(QCoreApplication.translate("save_fit_dialog", u"...", None))
        self.mode_group_box.setTitle(QCoreApplication.translate("save_fit_dialog", u"Mode", None))
        self.mode_add_rb.setText(QCoreApplication.translate("save_fit_dialog", u"ADD", None))
        self.mode_add_lbl.setText(QCoreApplication.translate("save_fit_dialog", u"Add new waypoints to the device without removing existing ones", None))
        self.mode_replace_rb.setText(QCoreApplication.translate("save_fit_dialog", u"REPLACE", None))
        self.mode_replace_lbl.setText(QCoreApplication.translate("save_fit_dialog", u"Replace all existing waypoints on the device", None))
        self.mode_delete_all_rb.setText(QCoreApplication.translate("save_fit_dialog", u"DELETE_ALL", None))
        self.mode_delete_all_lbl.setText(QCoreApplication.translate("save_fit_dialog", u"Delete all waypoints from the device", None))
    # retranslateUi

