from qgis.PyQt.QtWidgets import QWidget

from .select_section import select_sections,ch_to_id,zoom_to_selected
from .better_table_model import betterTableModel

from . import color_functions,table_view_to_csv,upload_routes_csv,file_dialogs
from .row_dialog import row_dialog,row_to_dict

from qgis.PyQt.QtSql import QSqlTableModel
from qgis.PyQt.QtCore import Qt
from qgis.utils import iface
#from PyQt5.QtGui import QMenu
from PyQt5.QtWidgets import QMenuBar,QMenu


import os

from qgis.core import QgsFieldProxyModel
from qgis.core import QgsMapLayerProxyModel

from qgis.PyQt import uic,QtGui
from qgis.PyQt.QtSql import QSqlQuery



def fixHeaders(path):
    with open(path) as f:
        t=f.read()
    r={'qgsfieldcombobox.h':'qgis.gui','qgsmaplayercombobox.h':'qgis.gui'}
    for i in r:
        t=t.replace(i,r[i])
    with open(path, "w") as f:
        f.write(t)
        
    
uiPath=os.path.join(os.path.dirname(__file__), 'routes_widget.ui')
fixHeaders(uiPath)
rw, _ = uic.loadUiType(uiPath)
    

'''
widget for making routes.
makes routes in table routes of database.
columns run varchar,f_line int,sec varchar,reversed bool,xsp varchar.

'''

class routes_widget(QWidget,rw):   
    #readings_box and network box are pre existing qgsmapLayerComboboxes. fieldboxes are preexisting. dd is database dialog.
    def __init__(self,parent,dd,table,readings_box,network_box,run_fieldbox,f_line_fieldbox,sec_fieldbox):
        super(QWidget,self).__init__(parent)
        self.setupUi(self)
        self.dd=dd
        self.table=table
        
        self.run_fieldbox=run_fieldbox
        self.f_line_fieldbox=f_line_fieldbox
        self.sec_fieldbox=sec_fieldbox
        
        self.network_box=network_box
        self.run_fieldbox=run_fieldbox
        self.readings_box=readings_box

        
        self.readings_box.layerChanged.connect(lambda layer:set_to(layer=layer,fb=self.run_fieldbox,name='run'))
        self.readings_box.layerChanged.connect(lambda layer:set_to(layer=layer,fb=self.f_line_fieldbox,name='f_line'))
        self.network_box.layerChanged.connect(lambda layer:set_to(layer=layer,fb=self.sec_fieldbox,name='sec'))

        self.run_fieldbox.setFilters(QgsFieldProxyModel.String)
        self.sec_fieldbox.setFilters(QgsFieldProxyModel.String)

        self.f_line_fieldbox.setFilters(QgsFieldProxyModel.Int)
        self.network_box.setFilters(QgsMapLayerProxyModel.LineLayer)
        self.readings_box.setFilters(QgsMapLayerProxyModel.LineLayer|QgsMapLayerProxyModel.PointLayer)

        self.add_button.clicked.connect(self.add_row_dlg)
        self.edit_button.clicked.connect(self.edit_row)
        self.autofit_run_button.clicked.connect(self.autofit_run)
        
        self.run_box.currentIndexChanged.connect(self.run_changed)

        self.dd.reconnected.connect(self.reconnect)
        dd.data_changed.connect(self.get_runs)
        self.refit_run_button.clicked.connect(self.refit_run)
        self.refit_all_button.clicked.connect(self.refit_all)
        
        self.top_menu=QMenuBar()
        self.layout().setMenuBar(self.top_menu)
        
        download_menu= self.top_menu.addMenu('Download...')
        self.download_route_act=download_menu.addAction('Download route as csv...')
        self.download_all_act=download_menu.addAction('Download all routes as csv...')

        self.download_route_act.triggered.connect(self.save_route)
        self.download_all_act.triggered.connect(self.save_routes)

        upload_menu= self.top_menu.addMenu('Upload...')
        self.upload_act=upload_menu.addAction('Upload routes csv(s)...')
        self.upload_act.triggered.connect(self.upload_routes)
        

        self.init_rows_menu()
        
        i=self.readings_box.findText('r')
        if i!=-1:
            self.readings_box.setLayer(self.readings_box.layer(i))

        i=self.network_box.findText('network')
        if i!=-1:
            self.network_box.setLayer(network_box.layer(i))
            

    def init_rows_menu(self):
        self.rows_menu = QMenu()
        self.route_view.setContextMenuPolicy(Qt.CustomContextMenu);
        self.route_view.customContextMenuRequested.connect(self.show_rows_menu)

        self.select_on_layers_act=self.rows_menu.addAction('select on layers')
        self.select_on_layers_act.triggered.connect(self.select_on_layers)

        self.select_from_layers_act=self.rows_menu.addAction('select from layers')
        self.select_from_layers_act.triggered.connect(self.select_from_layers)

        self.delete_rows_act=self.rows_menu.addAction('delete selected rows')
        self.delete_rows_act.triggered.connect(self.drop_selected_rows)

        
    def show_rows_menu(self,pt):
        self.rows_menu.exec_(self.mapToGlobal(pt))


    def select_from_layers(self):
        pass


    def check_connected(self):
        if self.dd.con:
            return True
        else:
            iface.messageBar().pushMessage('fitting tool: Not connected to database')
            return False

      
    def select_rows(self):
        for r in self.route_view.selectionModel().selectedRows():#indexes of column 0
            self.select_row(r)


    def refit_all(self):
        if self.check_connected():
            self.dd.refit_runs(self.dd.get_runs())  


    def refit_run(self):
        if self.check_connected():
            self.dd.refit_run(self.run_box.currentText())
         
    

#select section and points of readings layer if set
#i is index of 1st column
    def select_row(self,i):
        pass
        #self.route_model.i,


    def autofit_run(self):
        self.dd.autofit_run(self.run_box.currentText())
        self.route_model.select()
        iface.messageBar().pushMessage('fitting tool:autofit.')
        
        
    def reconnect(self):
        self.route_model=betterTableModel(db=self.dd.db)
        self.route_model.setColorFunction(color_functions.routes_color)
        self.route_model.setTable(self.table) 
        self.route_model.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.route_model.setSort(self.route_model.fieldIndex("s_line"),Qt.AscendingOrder)#sort by s
        
        self.route_view.setModel(self.route_model)
        self.route_view.setColumnHidden(self.route_model.fieldIndex("run"), True)#hide run column
        self.route_view.setColumnHidden(self.route_model.fieldIndex("pk"), True)#hide pk column

        self.route_view.resizeColumnsToContents()
        self.get_runs()
        self.run_changed(self.run_box.currentIndex())
        
    #sets run_box and returns list of runs
    def get_runs(self):
        self.run_box.clear()
        self.run_box.addItems(self.dd.get_runs())
        
    def save_route(self):
        s=file_dialogs.save_file_dialog('.csv',default_name=self.run_box.currentText())
        if s:
            table_view_to_csv.to_csv(self.route_view,s)#todo use quote charactor
            #self.dd.query_to_csv('select * from routes where run=%(run)s',{'run':self.run_box.currentText()},force_quote='*' )


    def save_routes(self):
        s=file_dialogs.save_file_dialog('.csv',default_name='routes.csv')
        if s:
            self.dd.download_routes(f)        


    def upload_routes(self):
        files=file_dialogs.load_files_dialog('.csv')
        iface.messageBar().pushMessage(str(files))
        sucessful=[]
        unsucessful=[]
        for f in files:
            try:
                self.dd.upload_route(f)
               # upload_routes_csv.upload_route(csv=f,con=self.dd.psycopg2_con())
                sucessful.append(f)

            except Exception as e:
                iface.messageBar().pushMessage('fitting tool: error uploading route:%s:%s'%(f,e),duration=5)
               # print 'fitting tool: error uploading route:%s:%s'%(f,e)
                unsucessful.append(f)
                
        iface.messageBar().pushMessage('fitting tool attempted to upload routes: sucessfull:%s. unsucessfull:%s'%(','.join(sucessful),','.join(unsucessful)))
        
        self.route_model.select()
            
            
    def add_row_dlg(self):
        #def __init__(self,dd,network_box,sec_fieldbox,readings_box,run_fieldbox,f_line_fieldbox,run_box,vals=None,parent=None):

        self.rd=row_dialog(self.dd,self.route_model,self.network_box,self.sec_fieldbox,self.readings_box,self.run_fieldbox,self.f_line_fieldbox,self.run_box,parent=self)
        self.rd.show()
        self.refresh_view()

        
    def refresh_view(self):
        self.route_model.select()
        self.route_view.viewport().update()
        

    def edit_row(self):
        i=self.route_view.selectionModel().selectedIndexes()[0]
                #    def __init__(self,dd,network_box,sec_fieldbox,readings_box,run_fieldbox,f_line_fieldbox,run_box,vals=None,parent=None):

        self.rd=row_dialog(self.dd,self.network_box,self.sec_fieldbox,self.readings_box,self.run_fieldbox,self.f_line_fieldbox,self.run_box,row_to_dict(i),self)
        self.rd.show()            
        self.refresh_view()
            

    def drop_selected_rows(self):
        self.drop_rows([r.row() for r in self.route_view.selectionModel().selectedRows()])


    #list of ints
    def drop_rows(self,rows):
        for row in sorted(rows, reverse=True):#bottom to top because deleting row changes index
            self.route_model.removeRow(row)
            
    #selects rows where section==sec
    def route_view_select(self,sec):
        inds=self.route_model.match(self.route_model.index(0,0),0,sec,-1)#list of model indexes where 1st col==sec 

        #enums
        cs=self.route_view.selectionModel().ClearAndSelect
        s=self.route_view.selectionModel().Select

        if len(inds)>0:
            self.route_view.selectionModel().select(inds[0],cs)#clear selected then select 1st one

            if len(inds)>2:
                #select rest of indexes
                for i in inds[1:]:
                    self.route_view.selectionModel().select(i,s)
                    
                    
    def run_changed(self,i):
        f="run='"+self.run_box.itemText(i)+"'"#filter like  ref='re'
        self.route_model.setFilter(f)
        self.route_model.select()
        self.route_view.setColumnHidden(self.route_model.fieldIndex("run"), True)#hide run column

        
    #select selected rows of routes table on layers
    def select_on_layers(self):
        inds=self.route_view.selectionModel().selectedRows()#indexes of column 0
        have_network=self.network_box.currentLayer() and self.sec_fieldbox.currentField()
        
        if have_network:
            select_sections([i.data() for i in inds],self.network_box.currentLayer(),self.sec_fieldbox.currentField(),zoom=True)

        if not have_network:
            iface.messageBar().pushMessage('fitting tool: Fields not set.')
            

        #select and zoom to features of readings layer    
        r_layer=self.readings_box.currentLayer()
        r_field=self.run_fieldbox.currentField()
        f_field=self.f_line_fieldbox.currentField()
        run=self.run_box.currentText()       
    
        s_col=self.route_model.fieldIndex('s_line')
        e_col=self.route_model.fieldIndex('e_line')
        
        ids=[ch_to_id(r_layer,r_field,run,f_field,i.sibling(i.row(),s_col).data(),i.sibling(i.row(),e_col).data()) for i in inds]#list of lists
        if ids:
            ids2=[]
            for i in ids:
                ids2+=i
                
            #r_layer.setSelectedFeatures(ids2)#qgis2
            r_layer.selectByIds(ids2)#qgis3
            zoom_to_selected(r_layer)

    
#sets layer of fieldbox fb to layer then tries to set fb to field with name name
def set_to(layer,fb,name=None):
    fb.setLayer(layer)
    fb.setField(name)
