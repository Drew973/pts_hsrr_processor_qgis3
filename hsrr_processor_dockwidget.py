#import traceback
import os

from PyQt5.QtWidgets import QDoubleSpinBox,QMessageBox,QComboBox,QUndoStack,QDockWidget,QMenu,QMenuBar
from PyQt5.QtSql import QSqlTableModel,QSqlQueryModel,QSqlDatabase
from PyQt5.QtGui import QDesktopServices

from qgis.PyQt.QtCore import pyqtSignal,Qt,QUrl#,QEvent
from qgis.utils import iface

from .betterTableModel import betterTableModel
from .dict_dialog import dictDialog
from .database_dialog.database_dialog import database_dialog
from . import (file_dialogs,changesModel,hsrrFieldsWidget,layerFunctions,runInfoModel,delegates,databaseFunctions
,undoableTableModel,commands)



import logging

logging.basicConfig(filename=r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\hsrrprocessor\hsrr_processor.log',
                    level=logging.INFO,filemode='w')

logger = logging.getLogger(__name__)




from . hsrrprocessor_dockwidget_base import Ui_fitterDockWidgetBase

class hsrrProcessorDockWidget(QDockWidget, Ui_fitterDockWidgetBase):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        super(hsrrProcessorDockWidget, self).__init__(parent)
        self.setupUi(self)
        print('hsrr processor __init__')
    
        self.connectDialog = database_dialog(self,'hsrrProcessorDb')

        self.undoStack = QUndoStack(self)

        self.addRowDialog = dictDialog(parent=self)
        w = QDoubleSpinBox(self.addRowDialog)
        w.setSingleStep(0.1)
        self.addRowDialog.addWidget('ch',w,True)
        self.addRowDialog.accepted.connect(self.addRow)
    
    
        self.setXspDialog = dictDialog(parent=self)
        w = QComboBox(self.setXspDialog)
        w.addItems(['CL1','CL2','CR1','CR2','RE','LE'])
        self.setXspDialog.addWidget('xsp',w,True)
        self.setXspDialog.accepted.connect(self.setXsp)  
    
        self.initRunInfoMenu()
        self.initRequestedMenu()
        self.initChangesMenu()
        self.initTopMenu()
        self.initFw()
    
        self.connectDialog.accepted.connect(self.connectToDatabase)   
        self.connectToDatabase(QSqlDatabase(),warning=False)#QSqlDatabase() will return default connection,
        self.runBox.setUndoStack(self.undoStack)
        self.runBox.description = 'change run'


    def initFw(self):
        self.fw = hsrrFieldsWidget.hsrrFieldsWidget(self)
        self.tabs.insertTab(0,self.fw,'Fields')
    
    
    
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
       
        
        self.connectRunInfo(db)
        self.connectCoverage(db)
        self.connectChangesModel(db)
        self.connectNetworkModel(db)
        self.undoStack.clear()


    def connectNetworkModel(self,db):
        self.networkModel = QSqlQueryModel(self)
        self.networkModel.setQuery('select sec from hsrr.network',db)
       # self.changesView.set delegates.secWidgetDelegate

        
    
    def connectChangesModel(self,db):    
        m = changesModel.changesModel(self,db,self.undoStack)
        
        self.runBox.currentTextChanged.connect(m.setRun)
        m.setRun(self.runBox.currentText())
        
        self.changesView.setModel(m)
        [self.changesView.setColumnHidden(col, True) for col in m.hiddenColIndexes]#hide run column
        self.changesView.resizeColumnsToContents()
        #self.changesView.setItemDelegateForColumn(self.changesModel.fieldIndex('sec'),delegates.lineEditRelationalDelegate())
        secCol = m.fieldIndex('sec')
        self.changesView.setItemDelegateForColumn(secCol,
            delegates.secWidgetDelegate(parent=self,fw=self.fw,model=m,column=secCol))          

        self.changesView.setItemDelegateForColumn(m.fieldIndex('ch'),
            delegates.chainageWidgetDelegate(parent=self,fw=self.fw))     

    
   # def connectSectionsModel(self,db):
    #    self.sectionsModel = QSqlQueryModel(db)
        
        

    def connectRunInfo(self,db):
        self.runsModel = runInfoModel.runInfoModel(parent=self,db=db,undoStack=self.undoStack)
        self.runsView.setModel(self.runsModel)
        self.runBox.setModel(self.runsModel)
        self.runBox.setCurrentIndex(0)
       # self.run_info_view.setItemDelegateForColumn(self.run_info_model.fieldIndex('file'),delegates.readOnlyText())#makes column uneditable
        
    
        
    def showAddDialog(self):
        if self.currentRun():
            self.addRowDialog.widget('ch').setValue(self.fw.lowestSelectedReading(self.currentRun()))
            self.addRowDialog.show()
    
    
    def addRow(self):
        data = {'run':self.currentRun(),'sec':None,'reversed':None,'xsp':None,'ch':self.addRowDialog['ch'],'note':None,'start_sec_ch':None,'end_sec_ch':None}
        #self.undoStack.push(changesModel.insertCommand(self.changesView.model(),[data],'add row'))
        
        #m = self.changesView.model()
        #self.undoStack.push(changesModel.methodCommand(m.insert,[data],m.drop,'add row'))
        self.undoStack.push(self.changesView.model().insertCommand(data,'add row'))


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
        self.addRowAct.triggered.connect(self.showAddDialog)
        
        
        autofitMenu = self.fittingMenu.addMenu('Autofit')
        topoAutofitAct = autofitMenu.addAction('Topology based')
        topoAutofitAct.triggered.connect(self.topoAutofit)

        
        helpMenu = self.topMenu.addMenu('Help')
        openHelpAct = helpMenu.addAction('Open help')
        openHelpAct.setToolTip('Open help in your default web browser')
        openHelpAct.triggered.connect(self.openHelp)

        self.filterLayerButton.clicked.connect(self.filterReadingsLayer)
        
      
    def topoAutofit(self):
        m = self.changesView.model()
        self.undoStack.push(changesModel.methodCommand(m.topologyAutofit,None,m.deleteDicts,'topology based autofit'))
        

    def filterReadingsLayer(self):
        run = self.currentRun()
        if run:
            self.fw.filterReadingsLayer(run)


    def setXsp(self):
        self.undoStack.push(self.changesView.model().setXspCommand(self.setXspDialog['xsp']))
            
            

    def initChangesMenu(self):
        self.rows_menu = QMenu(self)
        self.rows_menu.setToolTipsVisible(True)
        
        self.changesView.setContextMenuPolicy(Qt.CustomContextMenu);
        self.changesView.customContextMenuRequested.connect(lambda pt:self.rows_menu.exec_(self.mapToGlobal(pt)))
          

        self.selectOnLayers_act=self.rows_menu.addAction('select on layers')
        self.selectOnLayers_act.setToolTip('select these rows on network and/or readings layers.')
        self.selectOnLayers_act.triggered.connect(self.selectOnLayers)

        #selectFromLayersAct = self.rows_menu.addAction('select from layers')
        #selectFromLayersAct.setToolTip('set selected rows from selected features of readings layer.')
  #      self.select_from_layers_act.triggered.connect(self.select_from_layers)

        self.deleteRowsAct = self.rows_menu.addAction('delete selected rows')
        self.deleteRowsAct.triggered.connect(self.dropSelectedChangesViewRows)


      
    def dropSelectedChangesViewRows(self):
        
        pkCol = self.changesView.model().fieldIndex('pk')
        pks = [{'pk':r.sibling(r.row(),pkCol).data()} for r in self.changesView.selectionModel().selectedRows()]
        #self.undoStack.push(changesModel.dropCommand(self.changesView.model(),pks))
        
       # m = self.changesView.model()
        #self.undoStack.push(changesModel.methodCommand(m.drop,pks,m.insert,'drop selected rows'))
        self.undoStack.push(undoableTableModel.deleteDictsCommand(self.changesView.model(),pks,'drop selected rows'))
    #select selected rows of routes table on layers
    
    
    
    def selectOnLayers(self):

        inds = self.getSelectedRows()
        
        if inds:
            
            #select on network
            secCol = self.changesView.model().fieldIndex('sec')
            sects = [i.sibling(i.row(),secCol).data() for i in inds] 
            sects = [s for s in sects if not s=='D']
            
            networkLayer = self.fw['network']
            secField = self.fw['label']
            
            if networkLayer and secField and sects:
                layerFunctions.selectByVals(sects, networkLayer, secField)
                
                layerFunctions.zoomToSelected(networkLayer)
       
            
           #select on readings        
            readingsLayer = self.fw['readings']
            s_chField = self.fw['s_ch']
            e_ch_Field = self.fw['e_ch']
            runField = self.fw['run']
            
            ch_field = self.changesView.model().fieldIndex('ch')
            
            if readingsLayer and s_chField and e_ch_Field:
                
                fids = []
                for i in inds:                    
                    
                    s = i.sibling(i.row(),ch_field).data()
                    
                    if i.row()<i.model().rowCount()-1:#0 indexed
                        e = i.sibling(i.row()+1,ch_field).data()
                        fids+=layerFunctions.readingsFids(readingsLayer,self.currentRun(),runField,s,s_chField,e,e_ch_Field)
                    
                    else:
                        fids+=layerFunctions.readingsFids2(layer=readingsLayer,run=self.currentRun(),runField=runField,ch=s,e_chField=e_ch_Field)
                        
            
                readingsLayer.selectByIds(fids)  
        
                #only want to zoom to these if no section selected
                if not sects:
                    layerFunctions.zoomToSelected(readingsLayer)
  
    
    
    #first index of selected rows
    def getSelectedRows(self):
        inds = self.changesView.selectionModel().selectedRows()
        if inds:
            return inds
        iface.messageBar().pushMessage('hsrr tool:no rows selected')    
    
    
    
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
        

    #1 set of readings
   # def uploadReadings(self,uri):
      #  try:
     #       self.undoStack.push(runInfoModel.uploadReadingsCommand(self.runsView.model(),uri))
     #       self.upload_log.appendPlainText('sucessfully uploaded %s\n'%(uri))
                                                
     #   except Exception as e:
      #      self.upload_log.appendPlainText('error uploading %s:\n%s\n'%(uri,str(e)))#traceback.format_exc()
                

    def uploadRunsDialog(self):
        files = file_dialogs.load_files_dialog('.xls','upload spreadsheets')
        if files:
            self.undoStack.push(commands.uploadRunsCommand(self.runsView.model(),files))
           # for f in files:
               # self.uploadReadings(f)
            
            
            
    def uploadFolderDialog(self):
        folder = file_dialogs.load_directory_dialog('.xls','upload all .xls in directory')
        if folder:
            self.undoStack.push(commands.uploadRunsCommand(self.runsView.model(),file_dialogs.filter_files(folder,'.xls')))
                
            
        
    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

        

    def connectCoverage(self,db):
       # self.requestedModel = QSqlTableModel(db=self.dd.db)
        self.requestedModel = betterTableModel(db=db)
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


