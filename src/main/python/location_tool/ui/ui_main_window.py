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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDockWidget, QHBoxLayout,
    QHeaderView, QMainWindow, QMenu, QMenuBar,
    QSizePolicy, QSpacerItem, QStatusBar, QTableWidget,
    QTableWidgetItem, QTextEdit, QToolBar, QToolButton,
    QVBoxLayout, QWidget)
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
        self.add_wpt_action.setMenuRole(QAction.MenuRole.NoRole)
        self.delete_wpt_action = QAction(MainWindow)
        self.delete_wpt_action.setObjectName(u"delete_wpt_action")
        self.delete_wpt_action.setMenuRole(QAction.MenuRole.NoRole)
        self.toggle_debug_log_action = QAction(MainWindow)
        self.toggle_debug_log_action.setObjectName(u"toggle_debug_log_action")
        self.toggle_debug_log_action.setCheckable(True)
        self.toggle_debug_log_action.setMenuRole(QAction.MenuRole.NoRole)
        self.scan_for_devices_action = QAction(MainWindow)
        self.scan_for_devices_action.setObjectName(u"scan_for_devices_action")
        self.scan_for_devices_action.setCheckable(True)
        self.scan_for_devices_action.setMenuRole(QAction.MenuRole.NoRole)
        self.import_file_action = QAction(MainWindow)
        self.import_file_action.setObjectName(u"import_file_action")
        self.import_file_action.setMenuRole(QAction.MenuRole.NoRole)
        self.download_locations_fit_action = QAction(MainWindow)
        self.download_locations_fit_action.setObjectName(u"download_locations_fit_action")
        self.download_locations_fit_action.setEnabled(False)
        self.download_locations_fit_action.setMenuRole(QAction.MenuRole.NoRole)
        self.upload_locations_fit_action = QAction(MainWindow)
        self.upload_locations_fit_action.setObjectName(u"upload_locations_fit_action")
        self.upload_locations_fit_action.setEnabled(False)
        self.upload_locations_fit_action.setMenuRole(QAction.MenuRole.NoRole)
        self.save_file_action = QAction(MainWindow)
        self.save_file_action.setObjectName(u"save_file_action")
        self.save_file_action.setMenuRole(QAction.MenuRole.NoRole)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_3 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.waypoint_table = QTableWidget(self.centralwidget)
        if (self.waypoint_table.columnCount() < 7):
            self.waypoint_table.setColumnCount(7)
        self.waypoint_table.setObjectName(u"waypoint_table")
        self.waypoint_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed|QAbstractItemView.EditTrigger.SelectedClicked)
        self.waypoint_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.waypoint_table.setIconSize(QSize(24, 24))
        self.waypoint_table.setShowGrid(False)
        self.waypoint_table.setCornerButtonEnabled(False)
        self.waypoint_table.setColumnCount(7)
        self.waypoint_table.horizontalHeader().setVisible(True)
        self.waypoint_table.horizontalHeader().setHighlightSections(False)
        self.waypoint_table.horizontalHeader().setStretchLastSection(True)
        self.waypoint_table.verticalHeader().setVisible(False)
        self.waypoint_table.verticalHeader().setMinimumSectionSize(40)

        self.verticalLayout_2.addWidget(self.waypoint_table)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.delete_wpt_btn = QToolButton(self.centralwidget)
        self.delete_wpt_btn.setObjectName(u"delete_wpt_btn")

        self.horizontalLayout.addWidget(self.delete_wpt_btn)

        self.add_wpt_btn = QToolButton(self.centralwidget)
        self.add_wpt_btn.setObjectName(u"add_wpt_btn")

        self.horizontalLayout.addWidget(self.add_wpt_btn)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.log_dock = QDockWidget(MainWindow)
        self.log_dock.setObjectName(u"log_dock")
        self.log_dock.setEnabled(True)
        self.log_dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
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
        self.menuBar.setGeometry(QRect(0, 0, 1046, 37))
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
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolBar.sizePolicy().hasHeightForWidth())
        self.toolBar.setSizePolicy(sizePolicy)
        self.toolBar.setMovable(False)
        self.toolBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        MainWindow.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolBar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuWaypoint.menuAction())
        self.menuBar.addAction(self.menuDevice.menuAction())
        self.menuBar.addAction(self.menuView.menuAction())
        self.menuFile.addAction(self.import_file_action)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.save_file_action)
        self.menuFile.addSeparator()
        self.menuWaypoint.addAction(self.add_wpt_action)
        self.menuWaypoint.addAction(self.delete_wpt_action)
        self.menuView.addAction(self.toggle_debug_log_action)
        self.menuDevice.addAction(self.scan_for_devices_action)
        self.menuDevice.addSeparator()
        self.menuDevice.addAction(self.download_locations_fit_action)
        self.menuDevice.addAction(self.upload_locations_fit_action)
        self.toolBar.addAction(self.import_file_action)
        self.toolBar.addAction(self.save_file_action)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.download_locations_fit_action)
        self.toolBar.addAction(self.upload_locations_fit_action)
        self.toolBar.addSeparator()

        self.retranslateUi(MainWindow)
        self.toggle_debug_log_action.toggled.connect(self.log_dock.setVisible)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"LocationsFITTool", None))
        self.add_wpt_action.setText(QCoreApplication.translate("MainWindow", u"Add Waypoint", None))
#if QT_CONFIG(shortcut)
        self.add_wpt_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+N", None))
#endif // QT_CONFIG(shortcut)
        self.delete_wpt_action.setText(QCoreApplication.translate("MainWindow", u"Delete Waypoint", None))
#if QT_CONFIG(shortcut)
        self.delete_wpt_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Backspace", None))
#endif // QT_CONFIG(shortcut)
        self.toggle_debug_log_action.setText(QCoreApplication.translate("MainWindow", u"Toggle Debug Log", None))
#if QT_CONFIG(shortcut)
        self.toggle_debug_log_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Shift+L", None))
#endif // QT_CONFIG(shortcut)
        self.scan_for_devices_action.setText(QCoreApplication.translate("MainWindow", u"Scan For Devices", None))
#if QT_CONFIG(shortcut)
        self.scan_for_devices_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Shift+S", None))
#endif // QT_CONFIG(shortcut)
        self.import_file_action.setText(QCoreApplication.translate("MainWindow", u"Import File", None))
#if QT_CONFIG(shortcut)
        self.import_file_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.download_locations_fit_action.setText(QCoreApplication.translate("MainWindow", u"Download", None))
#if QT_CONFIG(shortcut)
        self.download_locations_fit_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Shift+D", None))
#endif // QT_CONFIG(shortcut)
        self.upload_locations_fit_action.setText(QCoreApplication.translate("MainWindow", u"Upload", None))
#if QT_CONFIG(tooltip)
        self.upload_locations_fit_action.setToolTip(QCoreApplication.translate("MainWindow", u"Upload Locations.fit", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.upload_locations_fit_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Shift+U", None))
#endif // QT_CONFIG(shortcut)
        self.save_file_action.setText(QCoreApplication.translate("MainWindow", u"Save File", None))
        self.delete_wpt_btn.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.add_wpt_btn.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.log_dock.setWindowTitle(QCoreApplication.translate("MainWindow", u"Debug Log", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuWaypoint.setTitle(QCoreApplication.translate("MainWindow", u"Waypoint", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.menuDevice.setTitle(QCoreApplication.translate("MainWindow", u"Device", None))
    # retranslateUi

