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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDockWidget, QHeaderView,
    QMainWindow, QMenu, QMenuBar, QSizePolicy,
    QStatusBar, QTabWidget, QTableWidget, QTableWidgetItem,
    QTextEdit, QToolBar, QTreeView, QVBoxLayout,
    QWidget)
from . import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1046, 708)
        MainWindow.setStyleSheet(u"")
        MainWindow.setDockOptions(QMainWindow.DockOption.AllowTabbedDocks|QMainWindow.DockOption.AnimatedDocks)
        self.add_wpt_action = QAction(MainWindow)
        self.add_wpt_action.setObjectName(u"add_wpt_action")
        self.add_wpt_action.setMenuRole(QAction.NoRole)
        self.delete_wpt_action = QAction(MainWindow)
        self.delete_wpt_action.setObjectName(u"delete_wpt_action")
        self.delete_wpt_action.setMenuRole(QAction.NoRole)
        self.toggle_debug_log_action = QAction(MainWindow)
        self.toggle_debug_log_action.setObjectName(u"toggle_debug_log_action")
        self.toggle_debug_log_action.setCheckable(True)
        self.toggle_debug_log_action.setMenuRole(QAction.NoRole)
        self.scan_for_devices_action = QAction(MainWindow)
        self.scan_for_devices_action.setObjectName(u"scan_for_devices_action")
        self.scan_for_devices_action.setCheckable(True)
        self.import_file_action = QAction(MainWindow)
        self.import_file_action.setObjectName(u"import_file_action")
        self.download_locations_fit_action = QAction(MainWindow)
        self.download_locations_fit_action.setObjectName(u"download_locations_fit_action")
        self.download_locations_fit_action.setEnabled(False)
        self.upload_locations_fit_action = QAction(MainWindow)
        self.upload_locations_fit_action.setObjectName(u"upload_locations_fit_action")
        self.upload_locations_fit_action.setEnabled(False)
        self.save_file_action = QAction(MainWindow)
        self.save_file_action.setObjectName(u"save_file_action")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_3 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_waypoints_table = QWidget()
        self.tab_waypoints_table.setObjectName(u"tab_waypoints_table")
        self.verticalLayout_4 = QVBoxLayout(self.tab_waypoints_table)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.waypoint_table = QTableWidget(self.tab_waypoints_table)
        self.waypoint_table.setObjectName(u"waypoint_table")
        self.waypoint_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed|QAbstractItemView.EditTrigger.SelectedClicked)
        self.waypoint_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.waypoint_table.setIconSize(QSize(24, 24))

        self.verticalLayout_2.addWidget(self.waypoint_table)


        self.verticalLayout_4.addLayout(self.verticalLayout_2)

        self.tabWidget.addTab(self.tab_waypoints_table, "")
        self.tab_geodata_explorer = QWidget()
        self.tab_geodata_explorer.setObjectName(u"tab_geodata_explorer")
        self.verticalLayout_geodata = QVBoxLayout(self.tab_geodata_explorer)
        self.verticalLayout_geodata.setObjectName(u"verticalLayout_geodata")
        self.geodata_view = QTreeView(self.tab_geodata_explorer)
        self.geodata_view.setObjectName(u"geodata_view")
        self.geodata_view.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed)

        self.verticalLayout_geodata.addWidget(self.geodata_view)

        self.tabWidget.addTab(self.tab_geodata_explorer, "")

        self.verticalLayout_3.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.log_dock = QDockWidget(MainWindow)
        self.log_dock.setObjectName(u"log_dock")
        self.log_dock.setEnabled(True)
        self.log_dock.setFeatures(QDockWidget.DockWidgetFloatable|QDockWidget.DockWidgetMovable)
        self.log_dock_contents = QWidget()
        self.log_dock_contents.setObjectName(u"log_dock_contents")
        self.verticalLayout_log = QVBoxLayout(self.log_dock_contents)
        self.verticalLayout_log.setObjectName(u"verticalLayout_log")
        self.log_textedit = QTextEdit(self.log_dock_contents)
        self.log_textedit.setObjectName(u"log_textedit")
        self.log_textedit.setReadOnly(True)

        self.verticalLayout_log.addWidget(self.log_textedit)

        self.log_dock.setWidget(self.log_dock_contents)
        MainWindow.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.log_dock)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1046, 24))
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
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        self.toolBar.setMovable(True)
        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuWaypoint.menuAction())
        self.menuBar.addAction(self.menuDevice.menuAction())
        self.menuBar.addAction(self.menuView.menuAction())
        self.menuFile.addAction(self.import_file_action)
        self.menuFile.addAction(self.save_file_action)
        self.menuWaypoint.addAction(self.add_wpt_action)
        self.menuWaypoint.addAction(self.delete_wpt_action)
        self.menuView.addAction(self.toggle_debug_log_action)
        self.menuDevice.addAction(self.scan_for_devices_action)
        self.menuDevice.addAction(self.download_locations_fit_action)
        self.menuDevice.addAction(self.upload_locations_fit_action)
        self.toolBar.addAction(self.import_file_action)
        self.toolBar.addAction(self.save_file_action)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.add_wpt_action)
        self.toolBar.addAction(self.delete_wpt_action)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.download_locations_fit_action)
        self.toolBar.addAction(self.upload_locations_fit_action)

        self.retranslateUi(MainWindow)
        self.toggle_debug_log_action.toggled.connect(self.log_dock.setVisible)
        self.log_dock.visibilityChanged.connect(self.toggle_debug_log_action.setChecked)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"LocationsFITTool", None))
        self.add_wpt_action.setText(QCoreApplication.translate("MainWindow", u"Add Waypoint", None))
#if QT_CONFIG(tooltip)
        self.add_wpt_action.setToolTip(QCoreApplication.translate("MainWindow", u"Add a new waypoint", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.add_wpt_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+N", None))
#endif // QT_CONFIG(shortcut)
        self.delete_wpt_action.setText(QCoreApplication.translate("MainWindow", u"Delete Waypoint", None))
#if QT_CONFIG(tooltip)
        self.delete_wpt_action.setToolTip(QCoreApplication.translate("MainWindow", u"Delete selected waypoint(s)", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.delete_wpt_action.setShortcut(QCoreApplication.translate("MainWindow", u"Backspace", None))
#endif // QT_CONFIG(shortcut)
        self.toggle_debug_log_action.setText(QCoreApplication.translate("MainWindow", u"Show Log", None))
#if QT_CONFIG(tooltip)
        self.toggle_debug_log_action.setToolTip(QCoreApplication.translate("MainWindow", u"Toggle the debug log panel", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.toggle_debug_log_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+L", None))
#endif // QT_CONFIG(shortcut)
        self.scan_for_devices_action.setText(QCoreApplication.translate("MainWindow", u"Scan for Devices", None))
#if QT_CONFIG(tooltip)
        self.scan_for_devices_action.setToolTip(QCoreApplication.translate("MainWindow", u"Continuously scan for MTP devices", None))
#endif // QT_CONFIG(tooltip)
        self.import_file_action.setText(QCoreApplication.translate("MainWindow", u"Import File", None))
#if QT_CONFIG(tooltip)
        self.import_file_action.setToolTip(QCoreApplication.translate("MainWindow", u"Import from GPX or FIT file", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.import_file_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.download_locations_fit_action.setText(QCoreApplication.translate("MainWindow", u"Download Locations.fit", None))
#if QT_CONFIG(tooltip)
        self.download_locations_fit_action.setToolTip(QCoreApplication.translate("MainWindow", u"Download Locations.fit from device", None))
#endif // QT_CONFIG(tooltip)
        self.upload_locations_fit_action.setText(QCoreApplication.translate("MainWindow", u"Upload Locations.fit", None))
#if QT_CONFIG(tooltip)
        self.upload_locations_fit_action.setToolTip(QCoreApplication.translate("MainWindow", u"Upload Locations.fit to device", None))
#endif // QT_CONFIG(tooltip)
        self.save_file_action.setText(QCoreApplication.translate("MainWindow", u"Save File", None))
#if QT_CONFIG(tooltip)
        self.save_file_action.setToolTip(QCoreApplication.translate("MainWindow", u"Save current data to GPX or FIT file", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.save_file_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_waypoints_table), QCoreApplication.translate("MainWindow", u"Waypoints (Legacy Table)", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_geodata_explorer), QCoreApplication.translate("MainWindow", u"GeoData Explorer", None))
        self.log_dock.setWindowTitle(QCoreApplication.translate("MainWindow", u"Log", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuWaypoint.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.menuDevice.setTitle(QCoreApplication.translate("MainWindow", u"Device", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

