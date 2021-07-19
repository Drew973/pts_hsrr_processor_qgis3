from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal,Qt,QUrl#,QEvent
from qgis.PyQt.QtSql import QSqlTableModel

from qgis.utils import iface

from qgis.PyQt.QtWidgets import QMessageBox
import os

from .routes_widget import layer_functions

from PyQt5.QtWidgets import QDockWidget,QMenu,QMenuBar
from PyQt5.QtGui import QDesktopServices

from .routes_widget.routes_widget import routes_widget
#from .routes_widget.layer_functions import select_sections
from .routes_widget.better_table_model import betterTableModel
from .database_dialog.database_dialog import database_dialog
from . import hsrr_processor_dd,file_dialogs
from . import routes_model


from .dict_dialog import dictDialog

from PyQt5.QtWidgets import QLineEdit,QComboBox,QCheckBox,QDoubleSpinBox

from .import delegates

from PyQt5.QtSql import QSqlQuery,QSqlQueryModel


#from qgis.PyQt.QtWebKit import QWebView,QDesktopServices 

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

        self.dd=None
        self.rw=routes_widget(self,self.dd,'hsrr.routes',self.readings_box,self.network_box,self.run_fieldbox,self.f_line_fieldbox,self.sec_fieldbox)
        self.rw_placeholder.addWidget(self.rw)
          

        #self.tabs.insertTab(2,self.rw,'Fitting')
    
        
      #  self.open_help_button.clicked.connect(self.open_help)        
        self.init_run_menu()
        self.init_requested_menu()
        self.init_section_changes_menu()
        self.initTopMenu()
        
        
    def onConnectAct(self):
        db=database_dialog(self).exec_()
        
        
        
    def connect(self):
        db=database_dialog(self).exec_()
        try:
            self.dd=hsrr_processor_dd.hsrr_dd(db)
            self.rw.connect_to_dd(self.dd)
            self.dd.sql('set search_path to hsrr,public;')
            self.setWindowTitle('Connected to %s - HSRR Processer'%(db.databaseName()))
            self.connect_run_info()
            self.connect_coverage()
            self.refresh_run_info()





            #model for section changes
            self.routes_model = routes_model.routesModel(db)
            self.routes_view.setModel(self.routes_model)
            [self.routes_view.setColumnHidden(col, True) for col in self.routes_model.hiddenColIndexes]#hide run column
            
            
            
            self.changesModel = QSqlQueryModel(self)
            self.changesModel.setQuery('select * from hsrr.changes_view',self.dd.db)
            print('changesModel')
            
            self.changesView.setModel(self.changesModel)

            self.run_box.setModel(self.run_info_model)
            self.run_box.currentTextChanged.connect(self.routes_model.setRun)
            
            
        except Exception as e:
            iface.messageBar().pushMessage("could not connect to database. %s"%(str(e)),duration=4)
            self.setWindowTitle('Not connected - HSRR Processer')
            self.dd=None



    def new_row(self):
        d = dictDialog(parent=self)
        d.addWidget('sec',QLineEdit(),True)
        d.addWidget('reversed',QCheckBox(),True)
        xsp_box=QComboBox()
        xsp_box.addItems(['LE','CL1','CL2','CL3','RE'])
        d.addWidget('xsp',xsp_box,True)
        d.addWidget('ch',QDoubleSpinBox(),True)
        d.accepted.connect(lambda:self.routes_model.addRow(self.current_run(),d['sec'],d['reversed'],d['xsp'],d['ch']))
        d.exec()
            

        
    def initTopMenu(self):
        self.topMenu = QMenuBar()
        
        
        self.mainWidget.layout().setMenuBar(self.topMenu)
        #self.layout().setMenuBar(self.top_menu)
     #   self.layout().addWidget(self.top_menu)
       
        databaseMenu = self.topMenu.addMenu('Database')
        connectAct = databaseMenu.addAction('Connect to database')
        connectAct.triggered.connect(self.connect)
        newAct = databaseMenu.addAction('Setup database for hsrr')
        newAct.triggered.connect(self.prepareDatabase)     
        
        
        uploadMenu = self.topMenu.addMenu('Upload')
        uploadReadingsAct = uploadMenu.addAction('Upload readings spreadsheet...')
        uploadReadingsAct.triggered.connect(self.upload_runs_dialog)
        uploadReadingsFolderAct = uploadMenu.addAction('Upload all readings in folder...')
        uploadReadingsFolderAct.triggered.connect(self.upload_folder_dialog)        
        
       
        
        routesMenu = self.topMenu.addMenu('Section_changes')
        setXspAct = routesMenu.addAction('Set xsp of run...')
        addRowAct = routesMenu.addAction('Add row...')
        addRowAct.triggered.connect(self.new_row)
        
        helpMenu = self.topMenu.addMenu('Help')
        openHelpAct = helpMenu.addAction('open help')
        openHelpAct.setToolTip('Open help in your default web browser')
        openHelpAct.triggered.connect(self.open_help)


    def init_section_changes_menu(self):
        self.rows_menu = QMenu()
        self.rows_menu.setToolTipsVisible(True)
        
        self.routes_view.setContextMenuPolicy(Qt.CustomContextMenu);
        self.routes_view.customContextMenuRequested.connect(lambda pt:self.rows_menu.exec_(self.mapToGlobal(pt)))
          

        self.select_on_layers_act=self.rows_menu.addAction('select on layers')
        self.select_on_layers_act.setToolTip('select these rows on network and/or readings layers.')
        self.select_on_layers_act.triggered.connect(self.select_on_layers)

        self.select_from_layers_act=self.rows_menu.addAction('select from layers')
        self.select_from_layers_act.setToolTip('set selected rows from selected features of readings layer.')
  #      self.select_from_layers_act.triggered.connect(self.select_from_layers)

        self.delete_rows_act=self.rows_menu.addAction('delete selected rows')
        self.delete_rows_act.triggered.connect(lambda:self.routes_model.dropRows(self.routes_view.selectionModel().selectedRows()))

        self.add_menu=self.rows_menu.addMenu('add new row')
        self.row_after_act=self.add_menu.addAction('add empty row after last selected')
#        self.row_after_act.triggered.connect(self.add_empty_row)

        self.add_from_feats_act=self.add_menu.addAction('add new row from selected features')
 #       self.add_from_feats_act.triggered.connect(self.add_from_feats)
        
        
        
        
    #select selected rows of routes table on layers
    ###########################################################################################################
    def select_on_layers(self):

        inds = self.get_selected_rows()
        
        s_ch_col = self.get_s_ch_field()
        e_ch_col = self.get_e_ch_field()
        
        run_col = self.get_run_field()
        run = self.current_run()
        readings_layer = self.get_readings_layer()
        
        
        #fids = readings_layer.selectedFeatureIds()#use this to keep features selected
        fids = []
       
        ch_col = self.routes_model.fieldIndex('ch')
        
        for i in inds:
            s = i.sibling(i.row(),ch_col).data()
            e = i.sibling(i.row()+1,ch_col).data()
        
            if s and e:
                fids += [f.id() for f in layer_functions.ch_to_features(readings_layer, run, run_col, s, s_ch_col, e, e_ch_col)]
        
        print('%s,%s,%s'%(s_ch_col,e_ch_col,run_col))
        readings_layer.selectByIds(fids)
        
        
        self.select_on_network(inds)
        
        '''
        
        if self.network_box.currentLayer() and self.sec_fieldbox.currentField():
            layer_functions.select_sections([i.data() for i in inds],self.network_box.currentLayer(),self.sec_fieldbox.currentField(),zoom=True)

        else:
            iface.messageBar().pushMessage('fitting tool: Network layer/label field not set.')
            

        #select and zoom to features of readings layer    
        r_field=self.run_fieldbox.currentField()
        f_field=self.f_line_fieldbox.currentField()
        run=self.run_box.currentText()       
    
        s_col=self.routes_model.fieldIndex('s_line')
        e_col=self.routes_model.fieldIndex('e_line')
        
        ids=[layer_functions.ch_to_id(r_layer,r_field,run,f_field,i.sibling(i.row(),s_col).data(),i.sibling(i.row(),e_col).data()) for i in self.routes_view.selectionModel().selectedRows()]#list of lists
        if ids:
           # r_layer.setSelectedFeatures(ids2)#qgis2
            r_layer.selectByIds(ids)#qgis3
            layer_functions.zoom_to_selected(r_layer)
        '''    
    
    #select sections from routes_view.selectedRows()
    def select_on_network(self,inds): 
        ch_col = self.routes_model.fieldIndex('sec')
        sects = [i.sibling(i.row(),ch_col).data() for i in inds] 
        network_layer = self.get_network_layer()
        sec_field = self.get_sec_field()
        layer_functions.select_sections(sects,network_layer,sec_field,zoom=True)
        
        
        
        
    def get_network_layer(self,message=True):
        if self.network_box.currentLayer():
            return self.network_box.currentLayer()
        if message:
            iface.messageBar().pushMessage('hsrr tool:no network layer selected')
        

    def get_selected_rows(self):
        inds = self.routes_view.selectionModel().selectedRows()
        if inds:
            return inds
        iface.messageBar().pushMessage('hsrr tool:no rows selected')


    def get_sec_field(self,message=True):
        if self.sec_fieldbox.currentField():
            return self.sec_fieldbox.currentField()
        if message:
            iface.messageBar().pushMessage('hsrr tool:no section label field selected')
            
        
    def get_readings_layer(self,message=True):
        if self.readings_box.currentLayer():
           return self.readings_box.currentLayer()
        if message:
            iface.messageBar().pushMessage('hsrr tool:no readings layer selected')
            
        
    def get_s_ch_field(self):
        return 's_ch'        
        
    
    def get_e_ch_field(self):
        return 'e_ch'  
        
    
    def get_run_field(self,message=False):
        if self.run_fieldbox.currentField():
           return self.run_fieldbox.currentField()
        if message:
            iface.messageBar().pushMessage('hsrr tool: run field not set')
   
    
    def current_run(self,message=True):      
        if self.run_box.currentText():
           return self.run_box.currentText()
        if message:
            iface.messageBar().pushMessage('hsrr tool: no run selected')
                
    
    def coverage_show_all(self):
        self.requested_model.setFilter('')
        self.requested_model.select()
        
        
    def coverage_show_missing(self):
        self.requested_model.setFilter("coverage=0")
        self.requested_model.select()


#opens help/index.html in default browser
    def open_help(self):
        help_path=os.path.join(os.path.dirname(__file__),'help','overview.html')
        help_path='file:///'+os.path.abspath(help_path)
        QDesktopServices.openUrl(QUrl(help_path))
        

    def connect_run_info(self):
        self.run_info_model=QSqlTableModel(db=self.dd.db)
        self.run_info_model.setTable('hsrr.run_info')
        self.run_info_model.setSort(self.run_info_model.fieldIndex("run"),Qt.AscendingOrder)
        self.run_info_model.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.run_info_view.setModel(self.run_info_model)
        
       # self.run_info_view.setItemDelegateForColumn(self.run_info_model.fieldIndex('file'),delegates.readOnlyText())#makes column uneditable
        
        
        
    def check_connected(self):
        if self.dd:
            if self.dd.con:
                return True

        iface.messageBar().pushMessage('fitting tool: Not connected to database')
        return False


    def upload_runs(self,runs):
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


    def upload_runs_dialog(self):
        if self.check_connected():
            files=file_dialogs.load_files_dialog('.xls','upload spreadsheets')
            if files:
             #   for f in files:#?
                 #   self.upload_runs(files)
                self.upload_runs(files)
            
    def upload_folder_dialog(self):
        folder=file_dialogs.load_directory_dialog('.xls','upload all .xls in directory')
        if folder:
            self.upload_runs(file_dialogs.filter_files(folder,'.xls'))
                
            
        
    def closeEvent(self, event):
        if self.dd:
            self.dd.disconnect()        
        self.closingPlugin.emit()
        event.accept()
                

    def after_refit(self):
        self.coverage_model.select()
        

    def connect_coverage(self):
       # self.requested_model = QSqlTableModel(db=self.dd.db)
        self.requested_model=betterTableModel(db=self.dd.db)
        self.requested_model.setEditStrategy(QSqlTableModel.OnFieldChange)        
        self.requested_model.setTable('hsrr.requested')
        self.requested_model.setEditable(False)#set all cols uneditable
        self.requested_model.setColEditable(self.requested_model.fieldIndex("note"),True)#make note col editable

        self.requested_model.setSort(self.requested_model.fieldIndex("sec"),Qt.AscendingOrder)
        
        self.requested_view.setModel(self.requested_model)
        self.requested_view.setColumnHidden(self.requested_model.fieldIndex("pk"), True)#hide pk column
        
        self.show_all_button.clicked.connect(self.coverage_show_all)
        self.show_missing_button.clicked.connect(self.coverage_show_missing)
        self.rw.refit.connect(self.requested_model.select)
            
        if self.show_missing_button.isChecked():
            self.coverage_show_missing()
        else:
            self.coverage_show_all()

        self.requested_view.resizeColumnsToContents()

        
    def prepareDatabase(self):
        if self.check_connected():
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
    def drop_run(self):
        r=self.run_box.currentText()
        self.dd.sql("delete from run_info where run='{run}'",{'run':r})
        self.rw.get_runs()

            
#for requested view
    def init_run_menu(self):
        self.run_info_menu = QMenu()
        act=self.run_info_menu.addAction('drop run')
        act.triggered.connect(lambda:self.dd.drop_runs([str(i.data()) for i in self.run_info_view.selectionModel().selectedRows(0)]))# selectedRows(0) returns column 0 (sec)
        act.triggered.connect(self.refresh_run_info)# selectedRows(0) returns column 0 (sec)

        self.run_info_view.setContextMenuPolicy(Qt.CustomContextMenu);
        self.run_info_view.customContextMenuRequested.connect(self.show_run_info_menu)


#for requested view
    def init_requested_menu(self):
        self.requested_menu = QMenu()
        act=self.requested_menu.addAction('zoom to section')
        act.triggered.connect(lambda:self.select_on_network([i.data() for i in self.requested_view.selectionModel().selectedRows()]))
        self.requested_view.setContextMenuPolicy(Qt.CustomContextMenu);
        self.requested_view.customContextMenuRequested.connect(self.show_requested_menu)

        
    def show_run_info_menu(self,pt):
        self.run_info_menu.exec_(self.mapToGlobal(pt))


    def show_requested_menu(self,pt):
        self.requested_menu.exec_(self.mapToGlobal(pt))


    def refresh_run_info(self):
        self.run_info_model.select()
        self.rw.refresh_runs()


