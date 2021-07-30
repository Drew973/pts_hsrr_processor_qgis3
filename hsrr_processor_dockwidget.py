#import traceback
import os

from PyQt5.QtWidgets import QDoubleSpinBox,QMessageBox
from PyQt5.QtSql import QSqlTableModel,QSqlQueryModel,QSqlDatabase
from PyQt5.QtWidgets import QDockWidget,QMenu,QMenuBar
from PyQt5.QtGui import QDesktopServices

from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal,Qt,QUrl#,QEvent
from qgis.utils import iface

from .betterTableModel import betterTableModel
from .dict_dialog import dictDialog
from .database_dialog.database_dialog import database_dialog
from . import file_dialogs,changesModel,hsrrFieldsWidget,layerFunctions,runInfoModel,delegates,databaseFunctions



uiPath=os.path.join(os.path.dirname(__file__), 'hsrr_processor_dockwidget_base.ui')
FORM_CLASS, _ = uic.loadUiType(uiPath)


class hsrrProcessorDockWidget(QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        super(hsrrProcessorDockWidget, self).__init__(parent)
        self.setupUi(self)
        print('hsrr processor __init__')
    
        self.connectDialog = database_dialog(self,'hsrrProcessorDb')


        self.addRowDialog = dictDialog(parent=self)
        w = QDoubleSpinBox(self.addRowDialog)
        w.setSingleStep(0.1)
        self.addRowDialog.addWidget('ch',w,True)
        self.addRowDialog.accepted.connect(self.addRow)
    
        self.initRunInfoMenu()
        self.initRequestedMenu()
        self.initChangesMenu()
        self.initTopMenu()
        self.initFw()
    
    
        self.connectDialog.accepted.connect(self.connectToDatabase)   
        self.connectToDatabase(QSqlDatabase(),warning=False)#QSqlDatabase() will return default connection,


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
                


    def connectNetworkModel(self,db):
        self.networkModel = QSqlQueryModel(self)
        self.networkModel.setQuery('select sec from hsrr.network',db)
       # self.changesView.set delegates.secWidgetDelegate

        
    
    def connectChangesModel(self,db):    
        m = changesModel.changesModel(db)
        
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
        self.runsModel = runInfoModel.runInfoModel(parent=self,db=db)       
        self.runsView.setModel(self.runsModel)
        self.runBox.setModel(self.runsModel)
        self.runBox.setCurrentIndex(0)
       # self.run_info_view.setItemDelegateForColumn(self.run_info_model.fieldIndex('file'),delegates.readOnlyText())#makes column uneditable
        
    
        
    def showAddDialog(self):
        if self.currentRun():
            self.addRowDialog.widget('ch').setValue(self.fw.lowestSelectedReading(self.currentRun()))
            self.addRowDialog.show()
    
    
    def addRow(self):
        
        if self.changesView.model():
            self.changesView.model().addRow(run=self.currentRun(),ch=self.addRowDialog['ch'])
        else:
            iface.messageBar().pushMessage("Not connected to database.",duration=4)

        
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
        
        
        self.uploadMenu = self.topMenu.addMenu('Upload')
        uploadReadingsAct =  self.uploadMenu.addAction('Upload readings spreadsheet...')
        uploadReadingsAct.triggered.connect(self.uploadRunsDialog)
        uploadReadingsFolderAct =  self.uploadMenu.addAction('Upload all readings in folder...')
        uploadReadingsFolderAct.triggered.connect(self.uploadFolderDialog)        
        
        
        self.fittingMenu = self.topMenu.addMenu('Fitting')
        setXspAct = self.fittingMenu.addAction('Set xsp of run...')
        
        self.addRowAct = self.fittingMenu.addAction('Add row...')
        self.addRowAct.triggered.connect(self.showAddDialog)
        
        autofitAct = self.fittingMenu.addAction('autofit run')
        autofitAct.triggered.connect(self.autofit)

        
        helpMenu = self.topMenu.addMenu('Help')
        openHelpAct = helpMenu.addAction('Open help')
        openHelpAct.setToolTip('Open help in your default web browser')
        openHelpAct.triggered.connect(self.openHelp)

        self.filterLayerButton.clicked.connect(self.filterReadingsLayer)
        

    def filterReadingsLayer(self):
        run = self.currentRun()
        if run:
            self.fw.filterReadingsLayer(run)


    def autofit(self):
        self.changesView.model().autofit(self.getCurrentRun())


    def setXsp(self):
        self.currentRun()


    def initChangesMenu(self):
        self.rows_menu = QMenu(self)
        self.rows_menu.setToolTipsVisible(True)
        
        self.changesView.setContextMenuPolicy(Qt.CustomContextMenu);
        self.changesView.customContextMenuRequested.connect(lambda pt:self.rows_menu.exec_(self.mapToGlobal(pt)))
          

        self.selectOnLayers_act=self.rows_menu.addAction('select on layers')
        self.selectOnLayers_act.setToolTip('select these rows on network and/or readings layers.')
        self.selectOnLayers_act.triggered.connect(self.selectOnLayers)

        self.selecFromLayersAct=self.rows_menu.addAction('select from layers')
        self.selecFromLayersAct.setToolTip('set selected rows from selected features of readings layer.')
  #      self.select_from_layers_act.triggered.connect(self.select_from_layers)

        self.deleteRowsAct=self.rows_menu.addAction('delete selected rows')
        self.deleteRowsAct.triggered.connect(lambda:self.changesView.model().dropRows(self.changesView.selectionModel().selectedRows()))


        
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
                    e = i.sibling(i.row()+1,ch_field).data()
                    fids+=layerFunctions.readingsFids(readingsLayer,self.currentRun(),runField,s,s_chField,e,e_ch_Field)
            
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
        


    def uploadReadings(self,uri):
        con = self.connectDialog.get_con()
        if con:
            
            try:
                self.runsModel.uploadReadings(uri)
                
                self.upload_log.appendPlainText('sucessfully uploaded %s\n'%(uri))
                                                
            except Exception as e:
                self.upload_log.appendPlainText('error uploading %s:\n%s\n'%(uri,str(e)))#traceback.format_exc()
                

    def uploadRunsDialog(self):
        files = file_dialogs.load_files_dialog('.xls','upload spreadsheets')
        if files:
            for f in files:
                self.uploadReadings(f)
            
    def uploadFolderDialog(self):
        folder=file_dialogs.load_directory_dialog('.xls','upload all .xls in directory')
        if folder:
            for f in file_dialogs.filter_files(folder,'.xls'):
                self.uploadReadings(f)
                
            
        
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
        msgBox.setText("DON'T USE THIS PARTWAY THROUGH THE JOB! because this will erase any data in tables used by this plugin.");
        msgBox.setInformativeText("Continue?");
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No);
        msgBox.setDefaultButton(QMessageBox.No);
        i = msgBox.exec_()
            
        if i==QMessageBox.Yes:
            try:
                con = self.connectDialog.get_con()
                databaseFunctions.runSetupFile(con=con,file='setup.txt',folder=os.path.join(os.path.dirname(__file__),'database'))
                iface.messageBar().pushMessage('fitting tool: prepared database')            

                
            except Exception as e:
                iface.messageBar().pushMessage(str(e))
                
   


#for requested view
    def initRunInfoMenu(self):
        self.runInfoMenu = QMenu(self)
        a = self.runInfoMenu.addAction('drop run')
        a.triggered.connect(lambda:self.runsModel.dropRuns([str(i.data()) for i in self.runsView.selectionModel().selectedRows(0)]))# selectedRows(0) returns column 0 (sec)

        self.runsView.setContextMenuPolicy(Qt.CustomContextMenu);
        self.runsView.customContextMenuRequested.connect(lambda pt:self.runInfoMenu.exec_(self.mapToGlobal(pt)))


#for requested view
    def initRequestedMenu(self):
        self.requested_menu = QMenu()
        zoomAct = self.requested_menu.addAction('zoom to section')
      #  act.triggered.connect(lambda:self.select_on_network([i.data() for i in self.requested_view.selectionModel().selectedRows()]))
        self.requested_view.setContextMenuPolicy(Qt.CustomContextMenu);
        self.requested_view.customContextMenuRequested.connect(lambda pt:self.requested_menu.exec_(self.mapToGlobal(pt)))


