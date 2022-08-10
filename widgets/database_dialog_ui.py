# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'database_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DatabaseDialog(object):
    def setupUi(self, DatabaseDialog):
        DatabaseDialog.setObjectName("DatabaseDialog")
        DatabaseDialog.resize(1020, 441)
        self.verticalLayout = QtWidgets.QVBoxLayout(DatabaseDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_5 = QtWidgets.QLabel(DatabaseDialog)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout.addWidget(self.label_5)
        self.connectionsBox = QtWidgets.QComboBox(DatabaseDialog)
        self.connectionsBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.connectionsBox.setObjectName("connectionsBox")
        self.horizontalLayout.addWidget(self.connectionsBox)
        self.refreshButton = QtWidgets.QPushButton(DatabaseDialog)
        self.refreshButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.refreshButton.setObjectName("refreshButton")
        self.horizontalLayout.addWidget(self.refreshButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(DatabaseDialog)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.host = QtWidgets.QLineEdit(DatabaseDialog)
        self.host.setObjectName("host")
        self.horizontalLayout_2.addWidget(self.host)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(DatabaseDialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.database = QtWidgets.QLineEdit(DatabaseDialog)
        self.database.setText("")
        self.database.setObjectName("database")
        self.horizontalLayout_3.addWidget(self.database)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_3 = QtWidgets.QLabel(DatabaseDialog)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)
        self.user = QtWidgets.QLineEdit(DatabaseDialog)
        self.user.setObjectName("user")
        self.horizontalLayout_4.addWidget(self.user)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_4 = QtWidgets.QLabel(DatabaseDialog)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_5.addWidget(self.label_4)
        self.password = QtWidgets.QLineEdit(DatabaseDialog)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setObjectName("password")
        self.horizontalLayout_5.addWidget(self.password)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.status = QtWidgets.QLabel(DatabaseDialog)
        self.status.setObjectName("status")
        self.verticalLayout.addWidget(self.status)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.testButton = QtWidgets.QPushButton(DatabaseDialog)
        self.testButton.setObjectName("testButton")
        self.horizontalLayout_6.addWidget(self.testButton)
        self.okButton = QtWidgets.QPushButton(DatabaseDialog)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout_6.addWidget(self.okButton)
        self.cancelButton = QtWidgets.QPushButton(DatabaseDialog)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout_6.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.retranslateUi(DatabaseDialog)
        QtCore.QMetaObject.connectSlotsByName(DatabaseDialog)

    def retranslateUi(self, DatabaseDialog):
        _translate = QtCore.QCoreApplication.translate
        DatabaseDialog.setWindowTitle(_translate("DatabaseDialog", "Connect to database"))
        self.label_5.setText(_translate("DatabaseDialog", "Connections"))
        self.connectionsBox.setToolTip(_translate("DatabaseDialog", "<html><head/><body><p>Load details for saved Postgis connections.<br/></p></body></html>"))
        self.refreshButton.setToolTip(_translate("DatabaseDialog", "<html><head/><body><p>Refresh connections dropdown.</p></body></html>"))
        self.refreshButton.setText(_translate("DatabaseDialog", "Refresh"))
        self.label.setText(_translate("DatabaseDialog", "Host"))
        self.host.setToolTip(_translate("DatabaseDialog", "<html><head/><body><p>Changing these will not change stored settings for the connection. </p></body></html>"))
        self.label_2.setText(_translate("DatabaseDialog", "Database"))
        self.database.setToolTip(_translate("DatabaseDialog", "<html><head/><body><p>Changing these will not change stored settings for the connection.</p></body></html>"))
        self.label_3.setText(_translate("DatabaseDialog", "User"))
        self.user.setToolTip(_translate("DatabaseDialog", "<html><head/><body><p>Changing these will not change stored settings for the connection.</p></body></html>"))
        self.label_4.setText(_translate("DatabaseDialog", "Password"))
        self.password.setToolTip(_translate("DatabaseDialog", "<html><head/><body><p>Changing these will not change stored settings for the connection.</p></body></html>"))
        self.status.setText(_translate("DatabaseDialog", "not connected"))
        self.testButton.setText(_translate("DatabaseDialog", "Test"))
        self.okButton.setText(_translate("DatabaseDialog", "Ok"))
        self.cancelButton.setText(_translate("DatabaseDialog", "Cancel"))