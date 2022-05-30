#import traceback
import os

from PyQt5.QtWidgets import QMessageBox,QComboBox,QUndoStack,QDockWidget,QMenu,QMenuBar,QFileDialog
from PyQt5.QtSql import QSqlTableModel,QSqlDatabase
from PyQt5.QtGui import QDesktopServices

from qgis.PyQt.QtCore import pyqtSignal,Qt,QUrl#,QEvent
from qgis.utils import iface



from hsrr_processor.widgets import dict_dialog,hsrrFieldsWidget,add_row_dialog


 
from hsrr_processor.database_dialog.database_dialog import database_dialog
from hsrr_processor import databaseFunctions,commands

from hsrr_processor.models import changesModel,runInfoModel,betterTableModel,network_model,readings_model
from hsrr_processor.hsrr_processor_dockwidget_base import Ui_fitterDockWidgetBase

import logging


from PyQt5.QtWidgets import QDialog


logging.basicConfig(filename = os.path.join(os.path.dirname(__file__),'hsrr_processor.log'),
                    level=logging.INFO,filemode='w')

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
    
        self.connectDialog = database_dialog(self,'hsrrProcessorDb')

        self.undoStack = QUndoStack(self)
        
        self.initFw()
        
        self.addRowDialog = add_row_dialog.addRowDialog(parent=self)

        self.initNetworkModel()
        self.initReadingsModel()

    
        self.setXspDialog = dict_dialog.dictDialog(parent=self)
        w = QComboBox(self.setXspDialog)
        w.addItems(['CL1','CL2','CR1','CR2','LE','RE'])
        self.setXspDialog.addWidget('xsp',w,True)
        self.setXspDialog.accepted.connect(self.setXsp)  
    
        self.initRunInfoMenu()
        self.initRequestedMenu()
        self.initTopMenu()
    
        self.connectDialog.accepted.connect(self.connectToDatabase)   
        self.connectToDatabase(QSqlDatabase(),warning=False)#QSqlDatabase() will return default connection,
        self.runBox.setUndoStack(self.undoStack)
        self.runBox.description = 'change run'

        self.changesView.undoStack = self.undoStack
         
        self.runBox.currentIndexChanged.connect(self.runChange)
        
        self.nextRunButton.clicked.connect(self.nextRun)
        self.lastRunButton.clicked.connect(self.lastRun)
        


    def runChange(self,row):
        run = self.runBox.itemText(row)
        self.changesView.model().setRun(run)
        self.readingsModel.setRun(run)



    def nextRun(self):
        self.runBox.setCurrentIndex(self.runBox.currentIndex()+1)



    def lastRun(self):
        self.runBox.setCurrentIndex(self.runBox.currentIndex()-1)
        
        

    def initFw(self):
        self.fw = hsrrFieldsWidget.hsrrFieldsWidget(self)
        self.tabs.insertTab(0,self.fw,'Fields')
        self.changesView.fw = self.fw
    
    
    
    def connectToDatabase(self,db=None,warning=True):
        if not db:
            db = self.connectDialog.get_db()

        if not db.isOpen():
            db.open()
            
        if not db.isOpen():
            self.setWindowTitle('Not connected - HSRR Processer')
            self.fittingMenu.setEnabled(False)
            self.uploadMenu.setEnabled(False)       
            self.prepareAct.setEnabled(False)
            
            if warning:
                iface.messageBar().pushMessage('could not connect to database',duration=6)            
            
        else:
            self.setWindowTitle('Connected to %s - HSRR Processer'%(db.databaseName()))
           
            self.uploadMenu.setEnabled(True)            
            self.fittingMenu.setEnabled(True)
            self.prepareAct.setEnabled(True)
       
        
        self.connectChangesModel(db)#want runbox.currentTextChanged to trigger setRun.
        self.connectRunInfo(db)
        self.connectCoverage(db)
        
        self.networkModel.setDb(db)
        self.readingsModel.setDb(db)
        
        self.runChange(self.runBox.currentIndex())
        self.undoStack.clear()

        

    def connectChangesModel(self,db):
        self.changesModel = changesModel.changesModel(parent=self,db=db,undoStack=self.undoStack)
        self.changesModel.setNetworkModel(self.networkModel)
        self.changesModel.setReadingsModel(self.readingsModel)
        self.changesView.setChangesModel(self.changesModel)
        self.addRowDialog.setRouteModel(self.changesModel)



    def initReadingsModel(self):
        self.readingsModel = readings_model.readingsModel(parent=self)
        self.changesView.setReadingsModel(self.readingsModel)
        
        self.fw.getWidget('s_ch').fieldChanged.connect(self.readingsModel.setStartChainageField)
        self.readingsModel.setStartChainageField(self.fw.getWidget('s_ch').currentField())

        self.fw.getWidget('e_ch').fieldChanged.connect(self.readingsModel.setEndChainageField)
        self.readingsModel.setEndChainageField(self.fw.getWidget('e_ch').currentField())

        self.fw.getWidget('readings').layerChanged.connect(self.readingsModel.setLayer)
        self.readingsModel.setLayer(self.fw.getWidget('readings').currentLayer())

        self.fw.getWidget('run').fieldChanged.connect(self.readingsModel.setRunField)
        self.readingsModel.setRunField(self.fw.getWidget('run').currentField())

        self.addRowDialog.setReadingsModel(self.readingsModel)



    def initNetworkModel(self):
        self.networkModel = network_model.networkModel()
        
        self.fw.getWidget('label').fieldChanged.connect(self.networkModel.setField)
        self.networkModel.setField(self.fw.getWidget('label').currentField())
        
        self.fw.getWidget('network').layerChanged.connect(self.networkModel.setLayer)
        self.networkModel.setLayer(self.fw.getWidget('network').currentLayer())
        
      #  self.addRowDialog.setNetworkModel(self.networkModel)
        self.changesView.setNetworkModel(self.networkModel)



    def connectRunInfo(self,db):
        self.runsModel = runInfoModel.runInfoModel(parent=self,db=db,undoStack=self.undoStack)
        self.runsView.setModel(self.runsModel)
        self.runBox.setModel(self.runsModel)
        self.runBox.setCurrentIndex(0)
       # self.run_info_view.setItemDelegateForColumn(self.run_info_model.fieldIndex('file'),delegates.readOnlyText())#makes column uneditable
        
    
        
    def addRow(self):
        self.addRowDialog.refresh() 
        self.addRowDialog.show()
            
    

    def initTopMenu(self):
        self.topMenu = QMenuBar()
                
        self.mainWidget.layout().setMenuBar(self.topMenu)
        #self.layout().setMenuBar(self.top_menu)
     #   self.layout().addWidget(self.top_menu)
       
        databaseMenu = self.topMenu.addMenu('Database')
        connectAct = databaseMenu.addAction('Connect to database')
        connectAct.triggered.connect(self.connectDialog.show)
        self.prepareAct = databaseMenu.addAction('Setup database for hsrr')
        self.prepareAct.triggered.connect(self.prepareDatabase)     
        
        
        editMenu = self.topMenu.addMenu("Edit")
        editMenu.addAction(self.undoStack.createUndoAction(self))
        editMenu.addAction(self.undoStack.createRedoAction(self))
        
        
        self.uploadMenu = self.topMenu.addMenu('Upload')
        uploadReadingsAct =  self.uploadMenu.addAction('Upload readings spreadsheet...')
        uploadReadingsAct.triggered.connect(self.uploadRunsDialog)
        uploadReadingsFolderAct =  self.uploadMenu.addAction('Upload all readings in folder...')
        uploadReadingsFolderAct.triggered.connect(self.uploadFolderDialog)        
        
        self.fittingMenu = self.topMenu.addMenu('Fitting')
        setXspAct = self.fittingMenu.addAction('Set xsp of run...')
        setXspAct.triggered.connect(self.setXspDialog.show)
        
        self.addRowAct = self.fittingMenu.addAction('Add row...')
        self.addRowAct.triggered.connect(self.addRow)
        
        #autofit menu
        autofitMenu = self.fittingMenu.addMenu('Autofit')

        simpleAutofitAct = autofitMenu.addAction('Add all')
        simpleAutofitAct.triggered.connect(self.simpleAutofit)
     
        sequencialAutofitAct = autofitMenu.addAction('Sequencial score autofit')
        sequencialAutofitAct.triggered.connect(self.sequencialScoreAutofit)
        
        #help menu
        helpMenu = self.topMenu.addMenu('Help')
        openHelpAct = helpMenu.addAction('Open help')
        openHelpAct.setToolTip('Open help in your default web browser')
        openHelpAct.triggered.connect(self.openHelp)

        self.filterLayerButton.clicked.connect(self.filterReadingsLayer)
        
        
        
    def simpleAutofit(self):
        m = self.changesView.model()
        m.simpleAutofit()
        


    def sequencialScoreAutofit(self):
        m = self.changesView.model()
        m.sequencialScoreAutofit()



    def filterReadingsLayer(self):
        run = self.currentRun()
        if run:
            self.fw.filterReadingsLayer(run)



    def setXsp(self):
        self.undoStack.push(self.changesView.model().setXspCommand(self.setXspDialog['xsp']))
            
    
    
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
        


    def uploadRunsDialog(self):
        files = QFileDialog.getOpenFileNames(caption='Upload readings', filter='*'+'.xls'+';;*')[0]#pyqt5
        files = [os.path.normpath(f) for f in files]
        logger.info('files'+str(files))
        if files:
            self.undoStack.push(commands.uploadRunsCommand(self.runsView.model(),files))
                      
            
            
    def uploadFolderDialog(self):
        folder = QFileDialog.getExistingDirectory(caption='upload all .xls in directory')#pyqt5
        files = filterFiles(folder,'.xls')
        logger.info('files'+str(files))
     #   folder = file_dialogs.load_directory_dialog('.xls','upload all .xls in directory')
     
        if folder:
            self.undoStack.push(commands.uploadRunsCommand(self.runsView.model(),files))
                
            
        
    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

        

    def connectCoverage(self,db):
       # self.requestedModel = QSqlTableModel(db=self.dd.db)
        self.requestedModel = betterTableModel.betterTableModel(db=db)
        self.requestedModel.setEditStrategy(QSqlTableModel.OnFieldChange)        
        self.requestedModel.setTable('hsrr.requested')
        self.requestedModel.setEditable(False)#set all cols uneditable
        self.requestedModel.setColEditable(self.requestedModel.fieldIndex("note"),True)#make note col editable

        self.requestedModel.setSort(self.requestedModel.fieldIndex("sec"),Qt.AscendingOrder)
        
        self.requested_view.setModel(self.requestedModel)
        self.requested_view.setColumnHidden(self.requestedModel.fieldIndex("pk"), True)#hide pk column
        
        self.show_all_button.clicked.connect(self.coverage_show_all)
        self.show_missing_button.clicked.connect(self.coverageShowMissing)
            
        if self.show_missing_button.isChecked():
            self.coverageShowMissing()
        else:
            self.coverage_show_all()

        self.requested_view.resizeColumnsToContents()


        
    def prepareDatabase(self):
        msgBox = QMessageBox();
        msgBox.setInformativeText("Perform first time setup for database?");
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No);
        msgBox.setDefaultButton(QMessageBox.No);
        i = msgBox.exec_()
            
        if i==QMessageBox.Yes:
            with self.connectDialog.get_con() as con:
                folder = os.path.join(os.path.dirname(__file__),'database')
                file = os.path.join(folder,'setup.txt')
                databaseFunctions.runSetupFile(cur=con.cursor(),file=file,printCom=True,recursive=False)
                iface.messageBar().pushMessage('fitting tool: prepared database')



#for requested view
    def initRunInfoMenu(self):
        self.runInfoMenu = QMenu(self)
        dropRunAct = self.runInfoMenu.addAction('drop run')
        dropRunAct.triggered.connect(self.dropSelectedRuns)# selectedRows(0) returns column 0 (sec)

        self.runsView.setContextMenuPolicy(Qt.CustomContextMenu);
        self.runsView.customContextMenuRequested.connect(lambda pt:self.runInfoMenu.exec_(self.mapToGlobal(pt)))
        
        
        
    def dropSelectedRuns(self):
        runs = [str(i.data()) for i in self.runsView.selectionModel().selectedRows(0)]
        self.undoStack.push(commands.dropRunsCommand(runs=runs,runInfoModel=self.runsView.model(),sectionChangesModel=self.changesView.model(),description='drop runs'))
        
    

#for requested view
    def initRequestedMenu(self):
        self.requested_menu = QMenu()
        zoomAct = self.requested_menu.addAction('zoom to section')
     #  act.triggered.connect(lambda:self.select_on_network([i.data() for i in self.requested_view.selectionModel().selectedRows()]))
        self.requested_view.setContextMenuPolicy(Qt.CustomContextMenu);
        self.requested_view.customContextMenuRequested.connect(lambda pt:self.requested_menu.exec_(self.mapToGlobal(pt)))



