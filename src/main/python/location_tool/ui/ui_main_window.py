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
    QPushButton, QSizePolicy, QSpacerItem, QStatusBar,
    QTableWidget, QTableWidgetItem, QTextEdit, QToolBar,
    QVBoxLayout, QWidget)
from . import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1000, 615)
        MainWindow.setStyleSheet(u"QMainWindow{\n"
"font-family:sans-serif;\n"
"font-size: 12pt;\n"
"}\n"
"\n"
"QTextEdit {\n"
"font-family: \"SF Mono\";\n"
"}\n"
"\n"
"QHeaderView::section {\n"
"\n"
"\n"
"padding: 4px;\n"
"}")
        MainWindow.setIconSize(QSize(48, 48))
        MainWindow.setDockOptions(QMainWindow.DockOption.AllowTabbedDocks|QMainWindow.DockOption.AnimatedDocks)
        self.save_locations_fit_action = QAction(MainWindow)
        self.save_locations_fit_action.setObjectName(u"save_locations_fit_action")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave))
        self.save_locations_fit_action.setIcon(icon)
        self.save_locations_fit_action.setMenuRole(QAction.MenuRole.NoRole)
        self.add_wpt_action = QAction(MainWindow)
        self.add_wpt_action.setObjectName(u"add_wpt_action")
        icon1 = QIcon()
        if QIcon.hasThemeIcon(QIcon.ThemeIcon.ListAdd):
            icon1 = QIcon.fromTheme(QIcon.ThemeIcon.ListAdd)
        else:
            icon1.addFile(u":/ui_icons/ui_icons/circle-plus-solid.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.add_wpt_action.setIcon(icon1)
        self.add_wpt_action.setMenuRole(QAction.MenuRole.NoRole)
        self.delete_wpt_action = QAction(MainWindow)
        self.delete_wpt_action.setObjectName(u"delete_wpt_action")
        icon2 = QIcon()
        if QIcon.hasThemeIcon(QIcon.ThemeIcon.ListRemove):
            icon2 = QIcon.fromTheme(QIcon.ThemeIcon.ListRemove)
        else:
            icon2.addFile(u":/ui_icons/ui_icons/circle-minus-solid.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.delete_wpt_action.setIcon(icon2)
        self.delete_wpt_action.setMenuRole(QAction.MenuRole.NoRole)
        self.toggle_debug_log_action = QAction(MainWindow)
        self.toggle_debug_log_action.setObjectName(u"toggle_debug_log_action")
        self.toggle_debug_log_action.setCheckable(True)
        self.toggle_debug_log_action.setMenuRole(QAction.MenuRole.NoRole)
        self.scan_for_devices_action = QAction(MainWindow)
        self.scan_for_devices_action.setObjectName(u"scan_for_devices_action")
        self.scan_for_devices_action.setCheckable(True)
        icon3 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.NetworkWired))
        self.scan_for_devices_action.setIcon(icon3)
        self.scan_for_devices_action.setMenuRole(QAction.MenuRole.NoRole)
        self.import_file_action = QAction(MainWindow)
        self.import_file_action.setObjectName(u"import_file_action")
        icon4 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen))
        self.import_file_action.setIcon(icon4)
        self.import_file_action.setMenuRole(QAction.MenuRole.NoRole)
        self.download_locations_fit_action = QAction(MainWindow)
        self.download_locations_fit_action.setObjectName(u"download_locations_fit_action")
        icon5 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.GoDown))
        self.download_locations_fit_action.setIcon(icon5)
        self.download_locations_fit_action.setMenuRole(QAction.MenuRole.NoRole)
        self.upload_locations_fit_action = QAction(MainWindow)
        self.upload_locations_fit_action.setObjectName(u"upload_locations_fit_action")
        icon6 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.GoUp))
        self.upload_locations_fit_action.setIcon(icon6)
        self.upload_locations_fit_action.setMenuRole(QAction.MenuRole.NoRole)
        self.save_gpx_action = QAction(MainWindow)
        self.save_gpx_action.setObjectName(u"save_gpx_action")
        self.save_gpx_action.setIcon(icon)
        self.save_gpx_action.setMenuRole(QAction.MenuRole.NoRole)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_3 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.waypoint_group_box = QWidget(self.centralwidget)
        self.waypoint_group_box.setObjectName(u"waypoint_group_box")
        self.verticalLayout_2 = QVBoxLayout(self.waypoint_group_box)
#ifndef Q_OS_MAC
        self.verticalLayout_2.setSpacing(-1)
#endif
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.waypoint_table = QTableWidget(self.waypoint_group_box)
        if (self.waypoint_table.columnCount() < 7):
            self.waypoint_table.setColumnCount(7)
        self.waypoint_table.setObjectName(u"waypoint_table")
        self.waypoint_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed|QAbstractItemView.EditTrigger.SelectedClicked)
        self.waypoint_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.waypoint_table.setShowGrid(False)
        self.waypoint_table.setCornerButtonEnabled(False)
        self.waypoint_table.setColumnCount(7)
        self.waypoint_table.horizontalHeader().setVisible(True)
        self.waypoint_table.horizontalHeader().setMinimumSectionSize(100)
        self.waypoint_table.horizontalHeader().setHighlightSections(False)
        self.waypoint_table.horizontalHeader().setStretchLastSection(True)
        self.waypoint_table.verticalHeader().setVisible(False)
        self.waypoint_table.verticalHeader().setMinimumSectionSize(24)

        self.verticalLayout_2.addWidget(self.waypoint_table)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.add_wpt_btn = QPushButton(self.waypoint_group_box)
        self.add_wpt_btn.setObjectName(u"add_wpt_btn")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.add_wpt_btn.sizePolicy().hasHeightForWidth())
        self.add_wpt_btn.setSizePolicy(sizePolicy)
        self.add_wpt_btn.setIconSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.add_wpt_btn)

        self.delete_wpt_btn = QPushButton(self.waypoint_group_box)
        self.delete_wpt_btn.setObjectName(u"delete_wpt_btn")
        sizePolicy.setHeightForWidth(self.delete_wpt_btn.sizePolicy().hasHeightForWidth())
        self.delete_wpt_btn.setSizePolicy(sizePolicy)
        self.delete_wpt_btn.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.delete_wpt_btn.setIconSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.delete_wpt_btn)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.verticalLayout_3.addWidget(self.waypoint_group_box)

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
        self.menuBar.setGeometry(QRect(0, 0, 1000, 24))
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
        self.status_bar.setSizeGripEnabled(False)
        MainWindow.setStatusBar(self.status_bar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        self.toolBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        MainWindow.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolBar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuWaypoint.menuAction())
        self.menuBar.addAction(self.menuDevice.menuAction())
        self.menuBar.addAction(self.menuView.menuAction())
        self.menuFile.addAction(self.import_file_action)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.save_locations_fit_action)
        self.menuFile.addAction(self.save_gpx_action)
        self.menuFile.addSeparator()
        self.menuWaypoint.addAction(self.add_wpt_action)
        self.menuWaypoint.addAction(self.delete_wpt_action)
        self.menuView.addAction(self.toggle_debug_log_action)
        self.menuDevice.addAction(self.scan_for_devices_action)
        self.menuDevice.addSeparator()
        self.menuDevice.addAction(self.download_locations_fit_action)
        self.menuDevice.addAction(self.upload_locations_fit_action)
        self.toolBar.addAction(self.import_file_action)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.add_wpt_action)
        self.toolBar.addAction(self.delete_wpt_action)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.download_locations_fit_action)
        self.toolBar.addAction(self.upload_locations_fit_action)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.save_gpx_action)
        self.toolBar.addAction(self.save_locations_fit_action)

        self.retranslateUi(MainWindow)
        self.toggle_debug_log_action.toggled.connect(self.log_dock.setVisible)
        self.add_wpt_btn.clicked.connect(self.add_wpt_action.trigger)
        self.delete_wpt_btn.clicked.connect(self.delete_wpt_action.trigger)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"LocationsFITTool", None))
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
        self.toggle_debug_log_action.setText(QCoreApplication.translate("MainWindow", u"Toggle Debug Log", None))
#if QT_CONFIG(shortcut)
        self.toggle_debug_log_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+D", None))
#endif // QT_CONFIG(shortcut)
        self.scan_for_devices_action.setText(QCoreApplication.translate("MainWindow", u"Scan For Devices", None))
#if QT_CONFIG(shortcut)
        self.scan_for_devices_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+C", None))
#endif // QT_CONFIG(shortcut)
        self.import_file_action.setText(QCoreApplication.translate("MainWindow", u"Import File", None))
#if QT_CONFIG(shortcut)
        self.import_file_action.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+I", None))
#endif // QT_CONFIG(shortcut)
        self.download_locations_fit_action.setText(QCoreApplication.translate("MainWindow", u"Download", None))
        self.upload_locations_fit_action.setText(QCoreApplication.translate("MainWindow", u"Upload", None))
#if QT_CONFIG(tooltip)
        self.upload_locations_fit_action.setToolTip(QCoreApplication.translate("MainWindow", u"Upload Locations.fit", None))
#endif // QT_CONFIG(tooltip)
        self.save_gpx_action.setText(QCoreApplication.translate("MainWindow", u"Save GPX File", None))
        self.add_wpt_btn.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.delete_wpt_btn.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuWaypoint.setTitle(QCoreApplication.translate("MainWindow", u"Waypoint", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.menuDevice.setTitle(QCoreApplication.translate("MainWindow", u"Device", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

