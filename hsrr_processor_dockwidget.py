#import traceback
import os

from PyQt5.QtWidgets import QMessageBox,QComboBox,QUndoStack,QDockWidget,QMenu,QMenuBar,QFileDialog
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtGui import QDesktopServices

from qgis.PyQt.QtCore import pyqtSignal,Qt,QUrl#,QEvent
from qgis.utils import iface


from hsrr_processor.widgets import dict_dialog,add_row_dialog,postgres_dialog,hsrr_fields_dialog
from hsrr_processor.models import run_info_model,network_model,readings_model,coverage_model,commands
from hsrr_processor.hsrr_processor_dockwidget_base import Ui_fitterDockWidgetBase



from hsrr_processor.models.routes.main_routes_model import mainRoutesModel
from hsrr_processor import init_logging#importing this will restart log


from hsrr_processor.database import setup,connection

import logging
logger = logging.getLogger(__name__)



def filterFiles(folder,ext):
    res=[]
    for root, dirs, files in os.walk(folder):
        res+=[os.path.normpath(os.path.join(root,f)) for f in files if os.path.splitext(f)[-1]==ext]
    return res




class hsrrProcessorDockWidget(QDockWidget, Ui_fitterDockWidgetBase):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        super(hsrrProcessorDockWidget, self).__init__(parent)
        self.setupUi(self)
    
        self.connectDialog = postgres_dialog.postgresDialog(parent=self,testName=connection.testName)

        self.undoStack = QUndoStack(self)
                
        self.addRowDialog = add_row_dialog.addRowDialog(parent=self)#don't want this to be modal. can't click map.

        self.setNetworkModel(network_model.networkModel())
        self.setReadingsModel(readings_model.readingsModel(parent=self))

        self.setXspDialog = dict_dialog.dictDialog(parent=self)
        w = QComboBox(self.setXspDialog)
        w.addItems(['CL1','CL2','CR1','CR2','LE','RE'])
        self.setXspDialog.addWidget('xsp',w,True)
        self.setXspDialog.accepted.connect(self.setXsp)  
    
        self.initRunInfoMenu()
        self.initTopMenu()
    
        self.connectDialog.accepted.connect(self.databaseDialogAccepted)
        self.setDb(connection.getConnection())

        self.changesView.undoStack = self.undoStack
         
        self.runBox.currentIndexChanged.connect(self.runChange)
        
        self.nextRunButton.clicked.connect(self.runBox.increase)
        self.lastRunButton.clicked.connect(self.runBox.decrease)
        
        hsrr_fields_dialog.hsrrFieldsDialog(readingsModel=self.readingsModel(),networkModel=self.networkModel(),parent=self).accept()
        #set fields to dialog defaults without showing it.



    def runChange(self,row):
        run = self.runBox.itemText(row)
        self.routesModel().setRun(run)
        self.changesView.setColumnHidden(self.routesModel().fieldIndex('pk'),True)
        self.changesView.setColumnHidden(self.routesModel().fieldIndex('reversed'),True)
        self.changesView.setColumnHidden(self.routesModel().fieldIndex('run'),True)

        #QSqlQueryModel.setQuery() will reset columns and cause view to show all columns.
        self.readingsModel().setRun(run)


    
    def routesModel(self):
        return self.changesView.model()



#make new routesModel from db and set to this.
    def setRoutesDb(self,db):
        m = mainRoutesModel(parent=self,db=db)
        m.setUndoStack(self.undoStack)
        m.setNetworkModel(self.networkModel())
        m.setReadingsModel(self.readingsModel())
        self.changesView.setModel(m)
      
    
    
    def databaseDialogAccepted(self):
        logger.debug('databaseDialogAccepted')

        test = connection.getTestConnection()
        
        
        self.setDb(QSqlDatabase())#set to invalid database. important because some models store database.        
        QSqlDatabase.removeDatabase(connection.name)#will cause crash if anything has this QSqlDatabase as member


        db = QSqlDatabase.addDatabase('QPSQL',connection.name)
        db.setHostName(test.hostName())
        db.setDatabaseName(test.databaseName())
        db.setUserName(test.userName())
        db.setPassword(test.password())
        self.setDb(db)
    
    
    
#create models and connect to database.
#QSqlDatabase() creates invalid database
#change ui to show if connected.    
    def setDb(self,db):
        logger.debug('setDb')
        
        #try to open if not already open
        if not db.isOpen():
            db.open()

        
        #show on ui
        if not db.isOpen():
            self.setWindowTitle('Not connected - HSRR Processer')
            self.fittingMenu.setEnabled(False)
            self.uploadMenu.setEnabled(False)       
            self.prepareAct.setEnabled(False)
                
        else:
            self.setWindowTitle('Connected to %s - HSRR Processer'%(db.databaseName()))
            self.uploadMenu.setEnabled(True)            
            self.fittingMenu.setEnabled(True)
            self.prepareAct.setEnabled(True)
       
        self.undoStack.clear()

        self.setRoutesDb(db)
        self.setRunsDb(db)
        self.setCoverageDb(db)
        
        self.networkModel().select()#model queries database(connection.name).
        
        self.runChange(self.runBox.currentIndex())#set run to first in dropdown


        
    def readingsModel(self):
        return self._readingsModel
        
        
        
    def setReadingsModel(self,model):
        self._readingsModel = model
        
        


    def setNetworkModel(self,model):
        self._networkModel = model
        self.changesView.setNetworkModel(model)
        self.requestedView.setNetworkModel(model)
        
        
        
    def networkModel(self):
        return self._networkModel



    def runsModel(self):
        return self._runsModel
        
        
        
    def setRunsDb(self,db):
        self._runsModel = run_info_model.runInfoModel(parent=self,db=db)
        self._runsModel.setUndoStack(self.undoStack)
        self.runsView.setModel(self._runsModel)
        self.runBox.setModel(self._runsModel)
        self.runBox.setCurrentIndex(0)
       # self.run_info_view.setItemDelegateForColumn(self.run_info_model.fieldIndex('file'),delegates.readOnlyText())#makes column uneditable
        
    
        
    def addRow(self):
        if self.routesModel() is not None:
            sel = [i.row() for i in self.changesView.selectionModel().selectedRows()]
            if sel:
                self.addRowDialog.setIndex(self.routesModel().index(max(sel),self.routesModel().fieldIndex('end_run_ch')))
            else:
                self.addRowDialog.setIndex(self.routesModel().createIndex(0,self.routesModel().fieldIndex('end_run_ch')))
            self.addRowDialog.show()
            
    

    def initTopMenu(self):
        self.topMenu = QMenuBar()
                
        self.mainWidget.layout().setMenuBar(self.topMenu)

        settingsMenu = self.topMenu.addMenu('Settings')
        
        connectAct = settingsMenu.addAction('Connect to database...')
        connectAct.triggered.connect(self.connectDialog.show)
        
        self.prepareAct = settingsMenu.addAction('Setup database for hsrr...')
        self.prepareAct.triggered.connect(self.prepareDatabase)     
                
        setFieldsAct = settingsMenu.addAction('Set Layers and Fields...')
        setFieldsAct.triggered.connect(self.setFields)        
        
        editMenu = self.topMenu.addMenu("Edit")
        editMenu.addAction(self.undoStack.createUndoAction(self))
        editMenu.addAction(self.undoStack.createRedoAction(self))
        
        
        self.uploadMenu = self.topMenu.addMenu('Upload')
        uploadReadingsAct =  self.uploadMenu.addAction('Upload readings spreadsheets...')
        uploadReadingsAct.triggered.connect(self.uploadRuns)
        uploadReadingsFolderAct =  self.uploadMenu.addAction('Upload all readings in folder...')
        uploadReadingsFolderAct.triggered.connect(self.uploadFolder)        
        
        self.fittingMenu = self.topMenu.addMenu('Fitting')
        setXspAct = self.fittingMenu.addAction('Set xsp of run...')
        setXspAct.triggered.connect(self.setXspDialog.show)
        
        self.addRowAct = self.fittingMenu.addAction('Add row...')
        self.addRowAct.triggered.connect(self.addRow)
        
        #autofit menu
        autofitMenu = self.fittingMenu.addMenu('Autofit')

        simpleAutofitAct = autofitMenu.addAction('Add all')
        simpleAutofitAct.triggered.connect(self.simpleAutofit)
        
        
        leastCostAutofitAct = autofitMenu.addAction('Least cost autofit')
        leastCostAutofitAct.triggered.connect(self.leastCostAutofit)  
        
        
        #help menu
        helpMenu = self.topMenu.addMenu('Help')
        openHelpAct = helpMenu.addAction('Open help')
        openHelpAct.setToolTip('Open help in your default web browser')
        openHelpAct.triggered.connect(self.openHelp)

        self.filterLayerButton.clicked.connect(self.filterReadingsLayer)
        
        
        
    def simpleAutofit(self):
        self.routesModel().simpleAutofit()
        


    def leastCostAutofit(self):
        self.routesModel().leastCostAutofit()
        
        

    def filterReadingsLayer(self):
        self.readingsModel().filterLayer()    



    def setXsp(self):
        xsp = self.setXspDialog['xsp']
        self.routesModel().setXsp(xsp)
            
    
    
    #triggered by setFieldsAct
    def setFields(self):
        hsrr_fields_dialog.hsrrFieldsDialog(readingsModel=self.readingsModel(),networkModel=self.networkModel(),parent=self).exec_()
        #dialog sets model layers&fields
    

    def currentRun(self,message=True):      
        if self.runBox.currentText():
           return self.runBox.currentText()
        if message:
            iface.messageBar().pushMessage('hsrr tool: no run selected')
                
    
    
    def coverage_show_all(self):
        self.requestedModel.setFilter('')
        self.requestedModel.select()
        
        
        
    def coverageShowMissing(self):
        self.requestedModel.setFilter("coverage=0")
        self.requestedModel.select()



#opens help/index.html in default browser
    def openHelp(self):
        help_path=os.path.join(os.path.dirname(__file__),'help','overview.html')
        help_path='file:///'+os.path.abspath(help_path)
        QDesktopServices.openUrl(QUrl(help_path))
        


    def uploadRuns(self):
        if not self.runsModel() is None:
            files = QFileDialog.getOpenFileNames(caption='Upload readings', filter='*'+'.xls'+';;*')[0]#pyqt5
            files = [os.path.normpath(f) for f in files]
            if files:
                self.undoStack.push(commands.uploadRunsCommand(files=files,readingsModel=self.readingsModel(),runInfoModel=self.runsModel()))
            
            
            
    def uploadFolder(self):
        if not self.runsModel() is None:
            folder = QFileDialog.getExistingDirectory(caption='upload all .xls in directory')#pyqt5
            if folder:
                files = filterFiles(folder,'.xls')
                if files:
                    self.undoStack.push(commands.uploadRunsCommand(files=files,readingsModel=self.readingsModel(),runInfoModel=self.runsModel()))

         
            
        
    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

        

    def setCoverageDb(self,db):
        self.requestedModel = coverage_model.coverageModel(db=db,parent=self)
        self.requestedView.setModel(self.requestedModel)
        self.requestedView.setColumnHidden(self.requestedModel.fieldIndex("pk"), True)#hide pk column
        
        self.show_all_button.clicked.connect(self.coverage_show_all)
        self.show_missing_button.clicked.connect(self.coverageShowMissing)
            
        
        if self.show_missing_button.isChecked():
            self.coverageShowMissing()
        else:
            self.coverage_show_all()

        self.requestedView.resizeColumnsToContents()


        
    def prepareDatabase(self):
        msgBox = QMessageBox()
        msgBox.setInformativeText("Perform first time setup for database?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        i = msgBox.exec_()
            
        if i==QMessageBox.Yes:
            
            db = connection.getConnection()
            r = setup.setupDb(db)
           
            logger.debug('setup result:%s',r)
            
            if r==True:
                iface.messageBar().pushMessage('fitting tool: prepared database')
            else:
                iface.messageBar().pushMessage('fitting tool:error preparing database:'+str(r))



#for requested view
    def initRunInfoMenu(self):
        self.runInfoMenu = QMenu(self)
        dropRunAct = self.runInfoMenu.addAction('Drop selected runs')
        dropRunAct.triggered.connect(self.dropSelectedRuns)# selectedRows(0) returns column 0 (sec)
        self.runsView.setContextMenuPolicy(Qt.CustomContextMenu);
        self.runsView.customContextMenuRequested.connect(lambda pt:self.runInfoMenu.exec_(self.mapToGlobal(pt)))
        
        
        
    def dropSelectedRuns(self):
        runs = [str(i.data()) for i in self.runsView.selectionModel().selectedRows(0)]
        self.undoStack.push(commands.combinedDropRunsCommand(runs=runs,routeModel=self.routesModel(),readingsModel=self.readingsModel(),runInfoModel=self.runsModel()))
        
    #runs,routeModel,readingsModel,runInfoModel



#for requested view
   # def initRequestedMenu(self):
     #   self.requested_menu = QMenu()
     #   zoomAct = self.requested_menu.addAction('zoom to section')
     #  act.triggered.connect(lambda:self.select_on_network([i.data() for i in self.requested_view.selectionModel().selectedRows()]))
     #   self.requested_view.setContextMenuPolicy(Qt.CustomContextMenu);
    #    self.requested_view.customContextMenuRequested.connect(lambda pt:self.requested_menu.exec_(self.mapToGlobal(pt)))



