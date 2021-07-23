from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal,Qt,QUrl#,QEvent
from qgis.PyQt.QtSql import QSqlTableModel

from qgis.utils import iface

from qgis.PyQt.QtWidgets import QMessageBox
import os

from . import layerFunctions

from .betterTableModel import betterTableModel
from . import delegates

from PyQt5.QtWidgets import QDockWidget,QMenu,QMenuBar
from PyQt5.QtGui import QDesktopServices

#from .routes_widget.layer_functions import select_sections
from .database_dialog.database_dialog import database_dialog
from . import hsrr_processor_dd,file_dialogs
from . import changesModel

#from . import fieldsWidget



from . import hsrrFieldsWidget

import traceback


from .dict_dialog import dictDialog
from PyQt5.QtWidgets import QDoubleSpinBox



def fixHeaders(path):
    with open(path) as f:
        t=f.read()
    r={'qgsfieldcombobox.h':'qgis.gui','qgsmaplayercombobox.h':'qgis.gui'}
    for i in r:
        t=t.replace(i,r[i])
    with open(path, "w") as f:
        f.write(t)

uiPath=os.path.join(os.path.dirname(__file__), 'hsrr_processor_dockwidget_base.ui')
fixHeaders(uiPath)
FORM_CLASS, _ = uic.loadUiType(uiPath)


class hsrrProcessorDockWidget(QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        super(hsrrProcessorDockWidget, self).__init__(parent)
        self.setupUi(self)
    
        self.addRowDialog = dictDialog(parent=self)
        w = QDoubleSpinBox(self.addRowDialog)
        w.setSingleStep(0.1)
        self.addRowDialog.addWidget('ch',w,True)
        self.addRowDialog.accepted.connect(self.addRow)
    
        self.connectDialog = database_dialog(self)
        self.connectDialog.accepted.connect(self.connect)    
    
    
    
        self.initRunInfoMenu()
        self.initRequestedMenu()
        self.initChangesMenu()
        self.initTopMenu()
        self.initFw()
        self.disconnect()

        

    #def onConnectAct(self):
     #   db=database_dialog(self).exec_()
        

    def initFw(self):
        self.fw = hsrrFieldsWidget.hsrrFieldsWidget(self)
        self.tabs.insertTab(0,self.fw,'Fields')
        
    
    
    
    def connect(self):
        db = self.connectDialog.get_db()
        
        if not db.isOpen():
            db.open()
            
        if db.isOpen():
            
            try:
                self.dd = hsrr_processor_dd.hsrr_dd(db)
                self.dd.sql('set search_path to hsrr,public;')
                self.setWindowTitle('Connected to %s - HSRR Processer'%(db.databaseName()))
                self.connectRunInfo(db)
                self.connectCoverage(db)
                self.connectChangesModel(db)
                self.addRowAct.setEnabled(True)
    
            except:
                iface.messageBar().pushMessage("could not connect to database. %s"%(traceback.format_exc()),duration=6)
                self.disconnect()

        else:
            self.disconnect()
            

    def disconnect(self):
        self.setWindowTitle('Not connected - HSRR Processer')
        self.dd = None
        self.changesModel = None
        self.runsModel = None
        self.addRowAct.setEnabled(False)
        
    
    def connectChangesModel(self,db):    
        self.changesModel = changesModel.changesModel(db)
        
        self.runBox.currentTextChanged.connect(self.changesModel.setRun)
        self.changesModel.setRun(self.runBox.currentText())
        
        self.changesView.setModel(self.changesModel)
        [self.changesView.setColumnHidden(col, True) for col in self.changesModel.hiddenColIndexes]#hide run column
        self.changesView.resizeColumnsToContents()
        self.changesView.setItemDelegateForColumn(self.changesModel.fieldIndex('sec'),delegates.lineEditRelationalDelegate())    


   # def connectSectionsModel(self,db):
    #    self.sectionsModel = QSqlQueryModel(db)
        
        

    def connectRunInfo(self,db):
        self.runsModel = QSqlTableModel(parent=self,db=db)
        self.runsModel.setTable('hsrr.run_info')
        self.runsModel.setSort(self.runsModel.fieldIndex("run"),Qt.AscendingOrder)
        self.runsModel.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.runsModel.select()
        self.runInfoView.setModel(self.runsModel)
        self.runBox.setModel(self.runsModel)
        self.runBox.setCurrentIndex(1)
       # self.run_info_view.setItemDelegateForColumn(self.run_info_model.fieldIndex('file'),delegates.readOnlyText())#makes column uneditable
        
    
        
    def showAddDialog(self):
        
        print(self.fw.lowestSelectedReading(self.currentRun()))
        self.addRowDialog.widget('ch').setValue(self.fw.lowestSelectedReading(self.currentRun()))
        self.addRowDialog.show()
    
    
    def addRow(self):
        if self.changesModel:
            self.changesModel.addRow(run=self.currentRun(),ch=self.addRowDialog['ch'])
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
        newAct = databaseMenu.addAction('Setup database for hsrr')
        newAct.triggered.connect(self.prepareDatabase)     
        
        
        uploadMenu = self.topMenu.addMenu('Upload')
        uploadReadingsAct = uploadMenu.addAction('Upload readings spreadsheet...')
        uploadReadingsAct.triggered.connect(self.uploadRunsDialog)
        uploadReadingsFolderAct = uploadMenu.addAction('Upload all readings in folder...')
        uploadReadingsFolderAct.triggered.connect(self.uploadFolderDialog)        
        
        routesMenu = self.topMenu.addMenu('Fitting')
        setXspAct = routesMenu.addAction('Set xsp of run...')
        self.addRowAct = routesMenu.addAction('Add row...')
        self.addRowAct.triggered.connect(self.showAddDialog)
        self.addRowAct.setEnabled(False)
        
        helpMenu = self.topMenu.addMenu('Help')
        openHelpAct = helpMenu.addAction('open help')
        openHelpAct.setToolTip('Open help in your default web browser')
        openHelpAct.triggered.connect(self.openHelp)


    def setXsp(self):
        self.currentRun()


    def initChangesMenu(self):
        self.rows_menu = QMenu()
        self.rows_menu.setToolTipsVisible(True)
        
        self.changesView.setContextMenuPolicy(Qt.CustomContextMenu);
        self.changesView.customContextMenuRequested.connect(lambda pt:self.rows_menu.exec_(self.mapToGlobal(pt)))
          

        self.selectOnLayers_act=self.rows_menu.addAction('select on layers')
        self.selectOnLayers_act.setToolTip('select these rows on network and/or readings layers.')
        self.selectOnLayers_act.triggered.connect(self.selectOnLayers)

        self.select_from_layers_act=self.rows_menu.addAction('select from layers')
        self.select_from_layers_act.setToolTip('set selected rows from selected features of readings layer.')
  #      self.select_from_layers_act.triggered.connect(self.select_from_layers)

        self.deleteRowsAct=self.rows_menu.addAction('delete selected rows')
        self.deleteRowsAct.triggered.connect(lambda:self.changesModel.dropRows(self.changesView.selectionModel().selectedRows()))

        self.add_menu=self.rows_menu.addMenu('add new row')
        self.row_after_act=self.add_menu.addAction('add empty row after last selected')
#        self.row_after_act.triggered.connect(self.add_empty_row)

        self.add_from_feats_act=self.add_menu.addAction('add new row from selected features')
 #       self.add_from_feats_act.triggered.connect(self.add_from_feats)
        
        
        
        
    #select selected rows of routes table on layers
    
    def selectOnLayers(self):

        inds = self.getSelectedRows()
        print([i.row() for i in inds])
        
        
        if inds:
            
            #select on network
            secCol = self.changesModel.fieldIndex('sec')
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
            
            ch_field=self.changesModel.fieldIndex('ch')
            
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
        

    def checkConnected(self):
        if self.dd:
            if self.dd.con:
                return True

        iface.messageBar().pushMessage('fitting tool: Not connected to database')
        return False


    def uploadRuns(self,runs):
        for f in runs:
            if self.dd.is_uploaded(f):
                self.upload_log.appendPlainText('%s is already uploaded\n'%(f))
            else:
                r=self.dd.upload_run_csv(f)
                if r==True:
                    self.upload_log.appendPlainText('sucessfully uploaded %s\n'%(f))
                else:
                    self.upload_log.appendPlainText('error uploading %s:%s\n'%(f,str(r)))
        self.update()
        self.refresh_run_info()


    def uploadRunsDialog(self):
        if self.checkConnected():
            files=file_dialogs.load_files_dialog('.xls','upload spreadsheets')
            if files:
             #   for f in files:#?
                 #   self.uploadRuns(files)
                self.uploadRuns(files)
            
    def uploadFolderDialog(self):
        folder=file_dialogs.load_directory_dialog('.xls','upload all .xls in directory')
        if folder:
            self.uploadRuns(file_dialogs.filter_files(folder,'.xls'))
                
            
        
    def closeEvent(self, event):
        if self.dd:
            self.dd.disconnect()        
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
        if self.checkConnected():
            msgBox=QMessageBox();
            msgBox.setText("DON'T USE THIS PARTWAY THROUGH THE JOB! because this will erase any data in tables used by this plugin.");
            msgBox.setInformativeText("Continue?");
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No);
            msgBox.setDefaultButton(QMessageBox.No);
            i=msgBox.exec_()
            if i==QMessageBox.Yes:
                self.dd.setup_database()
                iface.messageBar().pushMessage('fitting tool: prepared database')
                self.rw.connect_to_dd(self.dd)


    #drop selected run of run_info table
    def dropRun(self):
        r=self.runBox.currentText()
        self.dd.sql("delete from run_info where run='{run}'",{'run':r})
        self.rw.get_runs()

            
#for requested view
    def initRunInfoMenu(self):
        self.run_info_menu = QMenu()
        act=self.run_info_menu.addAction('drop run')
        act.triggered.connect(lambda:self.dd.drop_runs([str(i.data()) for i in self.run_info_view.selectionModel().selectedRows(0)]))# selectedRows(0) returns column 0 (sec)

        self.runInfoView.setContextMenuPolicy(Qt.CustomContextMenu);
        self.runInfoView.customContextMenuRequested.connect(lambda pt:self.run_info_menu.exec_(self.mapToGlobal(pt)))


#for requested view
    def initRequestedMenu(self):
        self.requested_menu = QMenu()
        act = self.requested_menu.addAction('zoom to section')
      #  act.triggered.connect(lambda:self.select_on_network([i.data() for i in self.requested_view.selectionModel().selectedRows()]))
        self.requested_view.setContextMenuPolicy(Qt.CustomContextMenu);
        self.requested_view.customContextMenuRequested.connect(lambda pt:self.requested_menu.exec_(self.mapToGlobal(pt)))


