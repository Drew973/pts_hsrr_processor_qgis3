from qgis.PyQt.QtWidgets import QWidget

from .better_table_model import betterTableModel

from . import color_functions,table_view_to_csv,upload_routes_csv,file_dialogs,layer_functions

from qgis.PyQt.QtSql import QSqlTableModel
from qgis.PyQt.QtCore import Qt
from qgis.utils import iface
#from PyQt5.QtGui import QMenu
from PyQt5.QtWidgets import QMenuBar,QMenu
from qgis.PyQt.QtCore import pyqtSignal

import os

from qgis.core import QgsFieldProxyModel
from qgis.core import QgsMapLayerProxyModel

from qgis.PyQt import uic,QtGui
from qgis.PyQt.QtSql import QSqlQuery

from PyQt5.Qt import QItemSelectionModel




from PyQt5.QtWidgets import QComboBox
# makes qComboBox b searchable
def make_searchable(b):
    b.setEditable(True)
    b.setInsertPolicy(QComboBox.NoInsert)
    b.lineEdit().editingFinished.connect(lambda:b.setCurrentText(b.itemText(b.currentIndex())))
    #editing finished triggered when lineEdit loses focus.
   


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
    refit = pyqtSignal()

    
    #readings_box and network box are pre existing qgsmapLayerComboboxes. fieldboxes are preexisting. dd is database dialog or None.
    def __init__(self,parent,dd,table,readings_box,network_box,run_fieldbox,f_line_fieldbox,sec_fieldbox,prefix='hsrr processor:'):
        super(QWidget,self).__init__(parent)
        self.setupUi(self)
        self.dd = dd
        self.table = table
        self.prefix = prefix
        self.run_fieldbox = run_fieldbox
        self.f_line_fieldbox = f_line_fieldbox
        self.sec_fieldbox = sec_fieldbox
        
        self.network_box = network_box
        self.run_fieldbox = run_fieldbox
        self.readings_box = readings_box
      
        self.readings_box.layerChanged.connect(lambda layer:set_to(layer=layer,fb=self.run_fieldbox,name='run'))
        self.readings_box.layerChanged.connect(lambda layer:set_to(layer=layer,fb=self.f_line_fieldbox,name='f_line'))
        self.network_box.layerChanged.connect(lambda layer:set_to(layer=layer,fb=self.sec_fieldbox,name='sec'))

        self.run_fieldbox.setFilters(QgsFieldProxyModel.String)
        self.sec_fieldbox.setFilters(QgsFieldProxyModel.String)

        self.f_line_fieldbox.setFilters(QgsFieldProxyModel.Int)
        self.network_box.setFilters(QgsMapLayerProxyModel.LineLayer)
        self.readings_box.setFilters(QgsMapLayerProxyModel.LineLayer|QgsMapLayerProxyModel.PointLayer)

        self.run_box.currentIndexChanged.connect(self.run_changed)

        #dd.data_changed.connect(self.refresh_runs)

        self.init_top_menu()

        self.filter_layer_button.clicked.connect(lambda:layer_functions.filter_by_run(self.readings_box.currentLayer(),self.run_fieldbox.currentField(),self.run_box.currentText()))
 
        self.init_rows_menu()
        set_layer_box_to(self.network_box,'network')
        set_layer_box_to(self.readings_box,'readings')
        make_searchable(self.run_box)        
        self.route_model = None



    def connect_to_dd(self,dd):
        self.dd=dd
        self.route_model=betterTableModel(db=self.dd.db)
            
        self.route_model.setColorFunction(color_functions.routes_color)
        self.route_model.setTable(self.table) 
        self.route_model.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.route_model.setSort(self.route_model.fieldIndex("s_line"),Qt.AscendingOrder)#sort by s
            
        self.route_view.setModel(self.route_model)
        self.route_view.setColumnHidden(self.route_model.fieldIndex("run"), True)#hide run column
        self.route_view.setColumnHidden(self.route_model.fieldIndex("pk"), True)#hide pk column

        self.route_view.resizeColumnsToContents()
        self.refresh_runs()
        self.run_changed(self.run_box.currentIndex())


    def init_top_menu(self):
        self.top_menu=QMenuBar()
        self.layout().setMenuBar(self.top_menu)

        download_menu= self.top_menu.addMenu('Download')
        self.download_route_act=download_menu.addAction('Download route as csv...')
        self.download_route_act.triggered.connect(self.save_route)
        self.download_all_act=download_menu.addAction('Download all routes as csv...')
        self.download_all_act.triggered.connect(self.save_routes)

        upload_menu= self.top_menu.addMenu('Upload')
        self.upload_act=upload_menu.addAction('Upload routes csv(s)...')
        self.upload_act.triggered.connect(self.upload_routes)

        refit_menu= self.top_menu.addMenu('Process')
        refit_menu.setToolTipsVisible(True)
        
        self.process_run_act=refit_menu.addAction('Process run')
        self.process_run_act.setToolTip('(Re)make fitted and resized tables for this run.')
        self.process_run_act.triggered.connect(self.process_run)
        
        self.refit_all_act=refit_menu.addAction('Process all runs')
        self.refit_all_act.setToolTip('(Re)make fitted and resized tables for all runs.')
        self.refit_all_act.triggered.connect(self.process_all)
    
        automake_menu= self.top_menu.addMenu('Automake')
        automake_menu.setToolTipsVisible(True)

        self.automake_act=automake_menu.addAction('Automake run')
        self.automake_act.setToolTip("Automatically adds rows to route with note of 'Auto' .May remove rows note of 'Auto' .Adds all sections within distance and in correct direction. Likely to contain incorrect slip roads.")
        self.automake_act.triggered.connect(self.automake_run)                

        self.remove_slips_act=automake_menu.addAction('Remove slip roads')
        self.remove_slips_act.setToolTip("remove slip roads from this route")
        self.remove_slips_act.triggered.connect(self.remove_slips)


    def init_rows_menu(self):
        self.rows_menu = QMenu()
        self.rows_menu.setToolTipsVisible(True)
        
        self.route_view.setContextMenuPolicy(Qt.CustomContextMenu);
        self.route_view.customContextMenuRequested.connect(self.show_rows_menu)

        self.select_on_layers_act=self.rows_menu.addAction('select on layers')
        self.select_on_layers_act.setToolTip('select these rows on network and/or readings layers.')
        self.select_on_layers_act.triggered.connect(self.select_on_layers)

        self.select_from_layers_act=self.rows_menu.addAction('select from layers')
        self.select_from_layers_act.setToolTip('set selected rows from selected features of readings layer.')
        self.select_from_layers_act.triggered.connect(self.select_from_layers)

        self.delete_rows_act=self.rows_menu.addAction('delete selected rows')
        self.delete_rows_act.triggered.connect(self.drop_selected_rows)

        self.add_menu=self.rows_menu.addMenu('add new row')
        self.row_after_act=self.add_menu.addAction('add empty row after last selected')
        self.row_after_act.triggered.connect(self.add_empty_row)

        self.add_from_feats_act=self.add_menu.addAction('add new row from selected features')
        self.add_from_feats_act.triggered.connect(self.add_from_feats)


    def add_empty_row(self):
        ls=self.last_selected_row()
        if not ls:
            ls=0

        d={'run':self.current_run()}
        s_line=self.route_model.index(ls,self.route_model.fieldIndex('e_line')).data()  
        if s_line:
            d.update({'s_line':s_line})

        self.dd.insert_into_routes(d)
        self.route_model.select()
        

    def last_selected_row(self):
        rows=[r.row() for r in self.route_view.selectionModel().selectedRows()]
        if rows:
            return min(rows)

      
    def show_rows_menu(self,pt):
        self.rows_menu.exec_(self.mapToGlobal(pt))



    def pks_to_row(self,pks):
        #start=self.route_model.index(0,self.route_model.fieldIndex("pk"))       
        #inds=[self.route_model.match(start,Qt.EditRole,sec,hits=-1) for sec in sects]#items in column of start where data for role match
        pass





    def select_from_layers(self):
        pks=[]


        f_line_field = self.f_line_fieldbox.currentField()
        run_field = self.run_fieldbox.currentField()

        if f_line_field and run_field:
            
            f_lines=[f[f_line_field] for f in self.readings_box.currentLayer().selectedFeatures() if f[run_field]==self.current_run()]
            print('f_lines: %s'%(f_lines))
            pks+=self.dd.f_lines_to_routes_pk(f_lines)
            

        sec_field = self.sec_fieldbox.currentField()
        if sec_field:
            pks+=self.dd.sects_to_routes_pk([f[sec_field] for f in self.network_box.currentLayer().selectedFeatures()])
        
    
        #selectRowsFromValues(self.route_view,self.route_model.fieldIndex('pk'),pks)
        print('pks:%s'%(pks))
        rows=self.route_model.findRows(pks,'pk')
        select_rows(self.route_view,rows,True)


    def add_from_feats(self):

        d={'run':self.current_run(),'note':'from feats'}
        
        sf=self.network_box.currentLayer().selectedFeatures()
        if len(sf)>1:
            iface.messageBar().pushMessage('fitting tool:more than 1 feature of network layer selected.')
            return
        if sf:
            d.update({'sec':sf[0][self.sec_fieldbox.currentField()]})

        sf=self.readings_box.currentLayer().selectedFeatures()

        if sf:
            f_lines=[f[self.f_line_fieldbox.currentField()] for f in sf if f[self.run_fieldbox.currentField()]==self.current_run()]#f_lines of features in run
            if f_lines:
                d.update({'s_line':min(f_lines),'e_line':max(f_lines)})           
        
        self.dd.insert_into_routes(d)
        self.route_model.select()
            

    def check_connected(self):
        if self.dd.con:
            return True
        else:
            iface.messageBar().pushMessage('fitting tool: Not connected to database')
            return False

    


#    def refit_all(self):
  #      if self.check_connected():
  #          self.dd.refit_all()  
 #           self.refit.emit()


    def process_run(self):
        if self.check_connected():
            self.dd.process_run(self.run_box.currentText())
            self.refit.emit()


    def process_all(self):
        if self.check_connected():
            self.dd.process_all()
            self.refit.emit()
    

#select section and points of readings layer if set
#i is index of 1st column
    def select_row(self,i):
        pass
        #self.route_model.i,


    def automake_run(self):
        self.dd.autofit_run(self.current_run())
        self.route_model.select()
        iface.messageBar().pushMessage('fitting tool:autofit.')


#might change run_box to subclass with search. May need to use something other than currentText()
    def current_run(self):
        return self.run_box.currentText()



    def remove_slips(self):
        self.dd.remove_slips(self.current_run())
        self.route_model.select()
        iface.messageBar().pushMessage('fitting tool:removed slip roads.')        


        
    #sets run_box
    def refresh_runs(self):
        self.run_box.clear()
        self.run_box.addItems(self.dd.get_runs())

        
    def save_route(self):
        s=file_dialogs.save_file_dialog('.csv',default_name=self.current_run())
        if s:
            self.dd.download_route(s,self.current_run())


    def save_routes(self):
        s=file_dialogs.save_file_dialog('.csv',default_name='routes.csv')
        if s:
            self.dd.download_routes(s)        


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


    def refresh_view(self):
        self.route_model.select()
        self.route_view.viewport().update()
        
           

    def drop_selected_rows(self):
        self.drop_rows([r.row() for r in self.route_view.selectionModel().selectedRows()])


    #list of ints
    def drop_rows(self,rows):
        for row in sorted(rows, reverse=True):#bottom to top because deleting row changes index
            self.route_model.removeRow(row)
        self.route_model.select()

    
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
        if self.route_model:
            f="run='"+self.run_box.itemText(i)+"'"#filter like  ref='re'
            self.route_model.setFilter(f)
            self.route_model.select()
            self.route_view.setColumnHidden(self.route_model.fieldIndex("run"), True)#hide run column

        
    #select selected rows of routes table on layers
    def select_on_layers(self):
        inds=self.route_view.selectionModel().selectedRows()#indexes of column 0
        have_network=self.network_box.currentLayer() and self.sec_fieldbox.currentField()
        
        if have_network:
            layer_functions.select_sections([i.data() for i in inds],self.network_box.currentLayer(),self.sec_fieldbox.currentField(),zoom=True)

        if not have_network:
            iface.messageBar().pushMessage('fitting tool: Fields not set.')
            

        #select and zoom to features of readings layer    
        r_layer=self.readings_box.currentLayer()
        r_field=self.run_fieldbox.currentField()
        f_field=self.f_line_fieldbox.currentField()
        run=self.run_box.currentText()       
    
        s_col=self.route_model.fieldIndex('s_line')
        e_col=self.route_model.fieldIndex('e_line')
        
        ids=[layer_functions.ch_to_id(r_layer,r_field,run,f_field,i.sibling(i.row(),s_col).data(),i.sibling(i.row(),e_col).data()) for i in inds]#list of lists
        if ids:
            ids2=[]
            for i in ids:
                ids2+=i
                
           # r_layer.setSelectedFeatures(ids2)#qgis2
            r_layer.selectByIds(ids2)#qgis3
            layer_functions.zoom_to_selected(r_layer)

    
#sets layer of fieldbox fb to layer then tries to set fb to field with name name
def set_to(layer,fb,name=None):
    fb.setLayer(layer)
    fb.setField(name)


#returns 1st layer in qgsMapLayerComboBox named name if exists
def layer_box_find(layer_box,name):
    i=layer_box.findText(name)
    if i!=-1:
        return layer_box.layer(i)

                
#set layer of qgsMapLayerComboBox to 1st layer named name if exists
def set_layer_box_to(layer_box,name):
    i=layer_box.findText(name)
    if i!=-1:
        layer_box.setLayer(layer_box.layer(i))




#select rows where column matches values
#qsqltableModel has no findItems method.
        
def selectRowsFromValues(tableView,column,values,clearSelection=True):
    model=tableView.model()
    
    items=[]
    for v in values:
        items+=model.findItems(v,column=column)
    
    indexes=[i.index() for i in items]

    for c in range(model.columnCount()):
        indexes += [i.siblingAtColumn(c) for i in indexes]#add indexes for second column
    
    
    tableView.selectionModel().clearSelection()
    for i in indexes:
        tableView.selectionModel().select(i,QItemSelectionModel.Select)


#rows is list of int
def select_rows(table_view,rows,clear=False):
    if clear:
        table_view.selectionModel().clearSelection()

    model = table_view.model()
    col_count = model.columnCount()

    indexes=[]
    for r in rows:
        indexes+=[model.index(r,c) for c in range(col_count)]
    
    #indexes = [[model.index(r,c) for c in range(col_count)] for r in rows]

    for i in indexes:
        table_view.selectionModel().select(i,QItemSelectionModel.Select)

        
    


