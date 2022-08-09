# -*- coding: utf-8 -*-
'''
Created on Wed Jul 13 08:09:47 2022

@author: Drew.Bennett


dialog to display postgres connections and create new connection.
dialog creates/replaces QSqlDatabase(dialog.testName) singleton when accepted or on test action.


after dialog closed can make new connection from this or dialog.makeDb(name)



'''
from PyQt5.QtCore import QSettings,Qt
from PyQt5.QtWidgets import QAction,QDialog
from PyQt5.QtSql import QSqlDatabase



from hsrr_processor.widgets import database_dialog_ui




class postgresDialog(QDialog,database_dialog_ui.Ui_DatabaseDialog):
    
        
    def __init__(self,testName='postgresDialog test connection',parent=None):        
        super(QDialog,self).__init__(parent=parent)
        self.setupUi(self)
 
        self.testName = testName
        self.displayDb(QSqlDatabase(self.testName))
        self.connectAct = QAction(self);
        self.connectAct.setShortcut(Qt.Key_Return)
        self.connectAct.triggered.connect(self.accept)
        self.okButton.clicked.connect(self.accept)

        self.connectionsBox.currentIndexChanged.connect(self.connectionsBoxChanged)

        self.testButton.clicked.connect(self.test)
        
        self.cancelButton.clicked.connect(self.reject)
        self.refreshButton.clicked.connect(self.refreshConnections)
        self.refreshConnections()
        
        
        
#sets text edits
    def setValues(self,host='',database='',user='',password=''):
        self.host.setText(host)
        self.database.setText(database)
        self.user.setText(user)
        self.password.setText(password)



#set test edits and status bar from db
    def displayDb(self,db):
        self.setValues(host=db.hostName(),database=db.databaseName(),user=db.userName(),password=db.password())

        if db.isOpen():
            self.status.setText('Connected to {name}'.format(name=db.databaseName()))
            
        else:
            self.status.setText('Not connected')



#replaces QSqlDatabase singleton QSqlDatabase(testName) from text edits . Anything using old connection should be deleted before calling this.

    def makeDb(self,name):
        QSqlDatabase.removeDatabase(name)
        db = QSqlDatabase.addDatabase('QPSQL',name)
        db.setHostName(self.host.text())
        db.setDatabaseName(self.database.text())
        db.setUserName(self.user.text())
        db.setPassword(self.password.text())
        db.open()
        return db
   
    

    def test(self):
        self.displayDb(self.makeDb(self.testName))#remove QSqlDatabase(self.name)



    def accept(self):
        self.test()
        super().accept()
        
        
    def refreshConnections(self):
        self.connectionsBox.clear()
        self.connectionsBox.addItems(getPostgresConnections())
        
        
        
    #sets edits to info for existing Qgis connection
    def connectionsBoxChanged(self,i):
        settings = QSettings()
        settings.beginGroup( '/PostgreSQL/connections/')
        settings.beginGroup(self.connectionsBox.itemText(i))#connection Name        
        self.host.setText(str(settings.value('host')))
        self.database.setText(str(settings.value('database')))
        self.user.setText(str(settings.value('username')))
        self.password.setText(str(settings.value('password')))

        
        
        
#finds postgres connections in qgis settings.
def getPostgresConnections():
    settings = QSettings()
    settings.beginGroup( '/PostgreSQL/connections/' )
    connections = settings.childGroups()
    settings.endGroup()
    return connections



if __name__=='__console__':
    d = postgresDialog()
    d.exec_()
