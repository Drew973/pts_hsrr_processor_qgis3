from qgis.PyQt import  QtGui, uic
from qgis.PyQt.QtCore import pyqtSignal,Qt,QUrl#,QEvent
from qgis.PyQt.QtSql import QSqlTableModel

from qgis.utils import iface

from qgis.PyQt.QtSql import QSqlQuery,QSqlQueryModel
from qgis.PyQt.QtWidgets import QMessageBox,QWhatsThis,QToolBar
import os

from os import path
import sys

from . import color_functions,hsrr_processor_dd,file_dialogs,copy_functions

from PyQt5.QtWidgets import QDockWidget,QMenu
from PyQt5.QtGui import QDesktopServices

from .routes_widget.routes_widget import routes_widget
from .routes_widget.layer_functions import select_sections
from .routes_widget.better_table_model import betterTableModel



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

        self.connect_button.clicked.connect(self.connect)
        self.dd=hsrr_processor_dd.hsrr_dd(self)

        self.prepare_database_button.clicked.connect(self.prepare_database)
          
        self.rw=routes_widget(self,self.dd,'hsrr.routes',self.readings_box,self.network_box,self.run_fieldbox,self.f_line_fieldbox,self.sec_fieldbox)

        self.rw_placeholder.addWidget(self.rw)
        #self.tabs.insertTab(2,self.rw,'Fitting')
        
        self.upload_csv_button.clicked.connect(self.upload_run_dialog)
        self.upload_folder_button.clicked.connect(self.upload_folder_dialog)
        
        self.open_help_button.clicked.connect(self.open_help)        
        self.init_run_menu()
        self.init_requested_menu()
        self.rw.refit.connect(lambda:print('refit'))
        
        
    def connect(self):
        if self.dd.exec_():
            if self.dd.connected:
                self.database_label.setText('Connected to %s'%(self.dd.db.databaseName()))
                self.connect_run_info()
                self.connect_coverage()
                self.refresh_run_info()
            else:
                self.database_label.setText('Not Connected')


    def coverage_show_all(self):
        self.requested_model.setFilter('')
        self.requested_model.select()
        
        
    def coverage_show_missing(self):
        self.requested_model.setFilter("coverage=0")
        self.requested_model.select()


#opens help/index.html in default browser
    def open_help(self):
        help_path=os.path.join(os.path.dirname(__file__),'help','index.html')
        help_path='file:///'+os.path.abspath(help_path)
        QDesktopServices.openUrl(QUrl(help_path))
        

    def connect_run_info(self):
        self.run_info_model=QSqlTableModel(db=self.dd.db)
        self.run_info_model.setTable('hsrr.run_info')
        self.run_info_model.setSort(self.run_info_model.fieldIndex("run"),Qt.AscendingOrder)
        self.run_info_model.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.run_info_view.setModel(self.run_info_model)
        
        
    def check_connected(self):
        if self.dd.con:
            return True
        else:
            iface.messageBar().pushMessage('fitting tool: Not connected to database')
            return False


    def upload_runs(self,runs):
        for f in runs:
            r=self.dd.upload_run_csv(f)
            if r==True:
                self.upload_log.appendPlainText('sucessfully uploaded %s'%(f))
            else:
                self.upload_log.appendPlainText('error uploading %s:%s'%(f,str(r)))
                self.update()
        self.refresh_run_info()


    def upload_run_dialog(self):
        if self.check_connected():
            files=file_dialogs.load_files_dialog('.xls','upload spreadsheet')
            if files:
                for f in files:
                    self.upload_runs(files)

            
    def upload_folder_dialog(self):
        folder=file_dialogs.load_directory_dialog('.xls','upload all .xls in directory')
        if folder:
            self.upload_runs(file_dialogs.filter_files(folder,'.xls'))
                
            
        
    def closeEvent(self, event):
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

        
    def prepare_database(self):
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



#select sec on network
    def select_on_network(self,sects):
       # inds=self.requested_view.selectionModel().selectedRows()#indexes of column 0
        have_network=self.network_box.currentLayer() and self.sec_fieldbox.currentField()
        
        if have_network:
            select_sections(sects,self.network_box.currentLayer(),self.sec_fieldbox.currentField(),zoom=True)

        else:
            iface.messageBar().pushMessage('fitting tool:network layer&section field not set')




