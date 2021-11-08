# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hsrr_processor_dockwidget_base.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_fitterDockWidgetBase(object):
    def setupUi(self, fitterDockWidgetBase):
        fitterDockWidgetBase.setObjectName("fitterDockWidgetBase")
        fitterDockWidgetBase.resize(559, 672)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(fitterDockWidgetBase.sizePolicy().hasHeightForWidth())
        fitterDockWidgetBase.setSizePolicy(sizePolicy)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.mainWidget = QtWidgets.QWidget(self.dockWidgetContents)
        self.mainWidget.setObjectName("mainWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.mainWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tabs = QtWidgets.QTabWidget(self.mainWidget)
        self.tabs.setObjectName("tabs")
        self.runs = QtWidgets.QWidget()
        self.runs.setObjectName("runs")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.runs)
        self.verticalLayout.setObjectName("verticalLayout")
        self.runsView = QtWidgets.QTableView(self.runs)
        self.runsView.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.runsView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.runsView.setObjectName("runsView")
        self.verticalLayout.addWidget(self.runsView)
        self.tabs.addTab(self.runs, "")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tab_5)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtWidgets.QLabel(self.tab_5)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.runBox = undoableComboBox(self.tab_5)
        self.runBox.setObjectName("runBox")
        self.horizontalLayout_3.addWidget(self.runBox)
        self.filterLayerButton = QtWidgets.QPushButton(self.tab_5)
        self.filterLayerButton.setObjectName("filterLayerButton")
        self.horizontalLayout_3.addWidget(self.filterLayerButton)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.changesView = changesView(self.tab_5)
        self.changesView.setAlternatingRowColors(True)
        self.changesView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.changesView.setObjectName("changesView")
        self.verticalLayout_4.addWidget(self.changesView)
        self.tabs.addTab(self.tab_5, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab_4)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.show_missing_button = QtWidgets.QRadioButton(self.tab_4)
        self.show_missing_button.setChecked(True)
        self.show_missing_button.setObjectName("show_missing_button")
        self.horizontalLayout_2.addWidget(self.show_missing_button)
        self.show_all_button = QtWidgets.QRadioButton(self.tab_4)
        self.show_all_button.setObjectName("show_all_button")
        self.horizontalLayout_2.addWidget(self.show_all_button)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.requested_view = QtWidgets.QTableView(self.tab_4)
        self.requested_view.setAlternatingRowColors(True)
        self.requested_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.requested_view.setObjectName("requested_view")
        self.verticalLayout_3.addWidget(self.requested_view)
        self.tabs.addTab(self.tab_4, "")
        self.verticalLayout_2.addWidget(self.tabs)
        self.verticalLayout_5.addWidget(self.mainWidget)
        fitterDockWidgetBase.setWidget(self.dockWidgetContents)

        self.retranslateUi(fitterDockWidgetBase)
        self.tabs.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(fitterDockWidgetBase)

    def retranslateUi(self, fitterDockWidgetBase):
        _translate = QtCore.QCoreApplication.translate
        fitterDockWidgetBase.setWindowTitle(_translate("fitterDockWidgetBase", "Not Connected - HSRR Processor"))
        self.runsView.setToolTip(_translate("fitterDockWidgetBase", "<html><head/><body><p>run_info table.</p></body></html>"))
        self.tabs.setTabText(self.tabs.indexOf(self.runs), _translate("fitterDockWidgetBase", "Runs"))
        self.label.setText(_translate("fitterDockWidgetBase", "run"))
        self.filterLayerButton.setToolTip(_translate("fitterDockWidgetBase", "<html><head/><body><p>Filter readings layer to this run.</p></body></html>"))
        self.filterLayerButton.setText(_translate("fitterDockWidgetBase", "Filter layer"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_5), _translate("fitterDockWidgetBase", "Fitting"))
        self.show_missing_button.setText(_translate("fitterDockWidgetBase", "Show missing"))
        self.show_all_button.setText(_translate("fitterDockWidgetBase", "Show all"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_4), _translate("fitterDockWidgetBase", "Coverage"))
from .undoableComboBox import undoableComboBox
from .widgets.changesView import changesView
