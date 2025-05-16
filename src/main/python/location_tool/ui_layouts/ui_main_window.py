# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QDockWidget, QGroupBox, QHBoxLayout,
    QHeaderView, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QSpacerItem, QStatusBar,
    QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(720, 662)
        font = QFont()
        font.setFamilies([u"SF Pro"])
        font.setPointSize(12)
        MainWindow.setFont(font)
        MainWindow.setStyleSheet(u"QWidget {\n"
"        font-family: \"SF Pro\";\n"
"        font-size: 12pt;\n"
"        }\n"
"\n"
"        QTextEdit {\n"
"        font-family: \"SF Mono\";\n"
"        font-size: 11pt;\n"
"        }\n"
"")
        MainWindow.setDockOptions(QMainWindow.DockOption.AllowTabbedDocks|QMainWindow.DockOption.AnimatedDocks)
        self.import_locations_fit_action = QAction(MainWindow)
        self.import_locations_fit_action.setObjectName(u"import_locations_fit_action")
        self.import_locations_fit_action.setMenuRole(QAction.MenuRole.NoRole)
        self.import_gpx_action = QAction(MainWindow)
        self.import_gpx_action.setObjectName(u"import_gpx_action")
        self.import_gpx_action.setMenuRole(QAction.MenuRole.NoRole)
        self.save_locations_fit_action = QAction(MainWindow)
        self.save_locations_fit_action.setObjectName(u"save_locations_fit_action")
        self.save_locations_fit_action.setMenuRole(QAction.MenuRole.NoRole)
        self.add_wpt_action = QAction(MainWindow)
        self.add_wpt_action.setObjectName(u"add_wpt_action")
        self.add_wpt_action.setMenuRole(QAction.MenuRole.NoRole)
        self.delete_wpt_action = QAction(MainWindow)
        self.delete_wpt_action.setObjectName(u"delete_wpt_action")
        self.delete_wpt_action.setMenuRole(QAction.MenuRole.NoRole)
        self.delete_all_wpts_action = QAction(MainWindow)
        self.delete_all_wpts_action.setObjectName(u"delete_all_wpts_action")
        self.delete_all_wpts_action.setMenuRole(QAction.MenuRole.NoRole)
        self.toggle_debug_log_action = QAction(MainWindow)
        self.toggle_debug_log_action.setObjectName(u"toggle_debug_log_action")
        self.toggle_debug_log_action.setCheckable(True)
        self.toggle_debug_log_action.setMenuRole(QAction.MenuRole.NoRole)
        self.scan_for_devices_action = QAction(MainWindow)
        self.scan_for_devices_action.setObjectName(u"scan_for_devices_action")
        self.scan_for_devices_action.setCheckable(True)
        self.scan_for_devices_action.setMenuRole(QAction.MenuRole.NoRole)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_7 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.file_btns_layout = QHBoxLayout()
        self.file_btns_layout.setObjectName(u"file_btns_layout")
        self.import_locations_fit_btn = QPushButton(self.centralwidget)
        self.import_locations_fit_btn.setObjectName(u"import_locations_fit_btn")

        self.file_btns_layout.addWidget(self.import_locations_fit_btn)

        self.import_gpx_btn = QPushButton(self.centralwidget)
        self.import_gpx_btn.setObjectName(u"import_gpx_btn")

        self.file_btns_layout.addWidget(self.import_gpx_btn)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.file_btns_layout.addItem(self.horizontalSpacer)

        self.save_locations_fit_btn = QPushButton(self.centralwidget)
        self.save_locations_fit_btn.setObjectName(u"save_locations_fit_btn")

        self.file_btns_layout.addWidget(self.save_locations_fit_btn)


        self.verticalLayout_7.addLayout(self.file_btns_layout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.waypoint_group_box = QGroupBox(self.centralwidget)
        self.waypoint_group_box.setObjectName(u"waypoint_group_box")
        self.verticalLayout_3 = QVBoxLayout(self.waypoint_group_box)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.waypoint_area = QVBoxLayout()
        self.waypoint_area.setObjectName(u"waypoint_area")
        self.waypoint_area.setContentsMargins(-1, -1, 0, -1)
        self.waypoint_table = QTableWidget(self.waypoint_group_box)
        self.waypoint_table.setObjectName(u"waypoint_table")

        self.waypoint_area.addWidget(self.waypoint_table)

        self.wpt_btns_layout = QHBoxLayout()
        self.wpt_btns_layout.setObjectName(u"wpt_btns_layout")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.wpt_btns_layout.addItem(self.horizontalSpacer_2)

        self.add_wpt_btn = QPushButton(self.waypoint_group_box)
        self.add_wpt_btn.setObjectName(u"add_wpt_btn")

        self.wpt_btns_layout.addWidget(self.add_wpt_btn)

        self.delete_wpt_btn = QPushButton(self.waypoint_group_box)
        self.delete_wpt_btn.setObjectName(u"delete_wpt_btn")

        self.wpt_btns_layout.addWidget(self.delete_wpt_btn)

        self.delete_all_wpts_btn = QPushButton(self.waypoint_group_box)
        self.delete_all_wpts_btn.setObjectName(u"delete_all_wpts_btn")

        self.wpt_btns_layout.addWidget(self.delete_all_wpts_btn)


        self.waypoint_area.addLayout(self.wpt_btns_layout)


        self.verticalLayout_3.addLayout(self.waypoint_area)


        self.horizontalLayout_2.addWidget(self.waypoint_group_box)


        self.verticalLayout_7.addLayout(self.horizontalLayout_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.log_dock = QDockWidget(MainWindow)
        self.log_dock.setObjectName(u"log_dock")
        self.log_dock.setEnabled(True)
        self.log_dock_contents = QWidget()
        self.log_dock_contents.setObjectName(u"log_dock_contents")
        self.log_dock_contents.setMinimumSize(QSize(0, 100))
        self.verticalLayout = QVBoxLayout(self.log_dock_contents)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.log_textedit = QTextEdit(self.log_dock_contents)
        self.log_textedit.setObjectName(u"log_textedit")

        self.verticalLayout.addWidget(self.log_textedit)

        self.log_dock.setWidget(self.log_dock_contents)
        MainWindow.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.log_dock)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 720, 24))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuWaypoint = QMenu(self.menuBar)
        self.menuWaypoint.setObjectName(u"menuWaypoint")
        self.menuView = QMenu(self.menuBar)
        self.menuView.setObjectName(u"menuView")
        self.menuDevice = QMenu(self.menuBar)
        self.menuDevice.setObjectName(u"menuDevice")
        MainWindow.setMenuBar(self.menuBar)
        self.status_bar = QStatusBar(MainWindow)
        self.status_bar.setObjectName(u"status_bar")
        MainWindow.setStatusBar(self.status_bar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuWaypoint.menuAction())
        self.menuBar.addAction(self.menuView.menuAction())
        self.menuBar.addAction(self.menuDevice.menuAction())
        self.menuFile.addAction(self.import_locations_fit_action)
        self.menuFile.addAction(self.import_gpx_action)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.save_locations_fit_action)
        self.menuFile.addSeparator()
        self.menuWaypoint.addAction(self.add_wpt_action)
        self.menuWaypoint.addAction(self.delete_wpt_action)
        self.menuWaypoint.addAction(self.delete_all_wpts_action)
        self.menuView.addAction(self.toggle_debug_log_action)
        self.menuDevice.addAction(self.scan_for_devices_action)

        self.retranslateUi(MainWindow)
        self.toggle_debug_log_action.toggled.connect(self.log_dock.setVisible)
        self.save_locations_fit_btn.clicked.connect(self.save_locations_fit_action.trigger)
        self.import_gpx_btn.clicked.connect(self.import_gpx_action.trigger)
        self.import_locations_fit_btn.clicked.connect(self.import_locations_fit_action.trigger)
        self.add_wpt_btn.clicked.connect(self.add_wpt_action.trigger)
        self.delete_all_wpts_btn.clicked.connect(self.delete_all_wpts_action.trigger)
        self.delete_wpt_btn.clicked.connect(self.delete_wpt_action.trigger)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"LocationsFITTool", None))
        self.import_locations_fit_action.setText(QCoreApplication.translate("MainWindow", u"Import Locations.fit", None))
#if QT_CONFIG(tooltip)
        self.import_locations_fit_action.setToolTip(QCoreApplication.translate("MainWindow", u"Import Waypoints from Locations.fit file", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.import_locations_fit_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.import_gpx_action.setText(QCoreApplication.translate("MainWindow", u"Import GPX", None))
#if QT_CONFIG(tooltip)
        self.import_gpx_action.setToolTip(QCoreApplication.translate("MainWindow", u"Import Waypoints from GPX file", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.import_gpx_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+L", None))
#endif // QT_CONFIG(shortcut)
        self.save_locations_fit_action.setText(QCoreApplication.translate("MainWindow", u"Save Locations.fit", None))
#if QT_CONFIG(tooltip)
        self.save_locations_fit_action.setToolTip(QCoreApplication.translate("MainWindow", u"Save Waypoints to new Locations.fit file", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.save_locations_fit_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.add_wpt_action.setText(QCoreApplication.translate("MainWindow", u"Add Waypoint", None))
#if QT_CONFIG(shortcut)
        self.add_wpt_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl++", None))
#endif // QT_CONFIG(shortcut)
        self.delete_wpt_action.setText(QCoreApplication.translate("MainWindow", u"Delete Waypoint", None))
#if QT_CONFIG(shortcut)
        self.delete_wpt_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Backspace", None))
#endif // QT_CONFIG(shortcut)
        self.delete_all_wpts_action.setText(QCoreApplication.translate("MainWindow", u"Delete All Waypoints", None))
#if QT_CONFIG(shortcut)
        self.delete_all_wpts_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Shift+Backspace", None))
#endif // QT_CONFIG(shortcut)
        self.toggle_debug_log_action.setText(QCoreApplication.translate("MainWindow", u"Toggle Debug Log", None))
#if QT_CONFIG(shortcut)
        self.toggle_debug_log_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+D", None))
#endif // QT_CONFIG(shortcut)
        self.scan_for_devices_action.setText(QCoreApplication.translate("MainWindow", u"Scan For Devices", None))
#if QT_CONFIG(shortcut)
        self.scan_for_devices_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+C", None))
#endif // QT_CONFIG(shortcut)
        self.import_locations_fit_btn.setText(QCoreApplication.translate("MainWindow", u"Import Locations.fit", None))
        self.import_gpx_btn.setText(QCoreApplication.translate("MainWindow", u"Import GPX", None))
        self.save_locations_fit_btn.setText(QCoreApplication.translate("MainWindow", u"Save Locations.fit", None))
        self.waypoint_group_box.setTitle(QCoreApplication.translate("MainWindow", u"Waypoints", None))
        self.add_wpt_btn.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.delete_wpt_btn.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.delete_all_wpts_btn.setText(QCoreApplication.translate("MainWindow", u"Delete All", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuWaypoint.setTitle(QCoreApplication.translate("MainWindow", u"Waypoint", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.menuDevice.setTitle(QCoreApplication.translate("MainWindow", u"Device", None))
    # retranslateUi

