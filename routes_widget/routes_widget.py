
from qgis.PyQt.QtCore import Qt,pyqtSignal
from qgis.utils import iface
#from PyQt5.QtGui import QMenu
from PyQt5.QtWidgets import QMenu
##from qgis.PyQt.QtCore import pyqtSignal

import os
from qgis.PyQt import uic
from PyQt5.Qt import QItemSelectionModel



from PyQt5.QtSql import QSqlRelationalDelegate
from . import delegates


from PyQt5.QtWidgets import QComboBox,QWidget
# makes qComboBox b searchable
def makeSearchable(b):
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
    def __init__(self,parent,model = None,runModel=None):
        super(QWidget,self).__init__(parent)
        self.setupUi(self)


        self.model = None
        
        
        self.setModel(model)
        self.setRunModel(runModel)    
        self.runBox.currentIndexChanged.connect(self.setRun)
        self.setRun(self.runBox.currentIndex())
        makeSearchable(self.runBox) 
        self.initRowsMenu()



    def setModel(self,model):
        self.model = model
        self.view.setModel(model)
        
        if model:
            #self.view.setItemDelegateForColumn(model.fieldIndex('sec'),QSqlRelationalDelegate(model)) 
            self.view.setItemDelegateForColumn(model.fieldIndex('sec'),delegates.searchableRelationalDelegate(model)) 
            self.view.hideColumn(model.fieldIndex('pk'))
            self.view.hideColumn(model.fieldIndex('run'))

        self.view.resizeColumnsToContents()

        
    
    def setRunModel(self,runsModel):
        self.runBox.setModel(runsModel)
        
        if runsModel:
            self.runBox.setModelColumn(runsModel.fieldIndex('run'))
            self.setRun(self.runBox.currentIndex())
    
    
    def setRun(self,i):
        print(self.model)
        
        if self.model:
            self.model.setRun(self.runBox.itemText(i))
    
    
    
    def deleteSelectedRows(self):
        pass
    
    
    def initRowsMenu(self):
        self.rowsMenu = QMenu()
        self.rowsMenu.setToolTipsVisible(True)
        
        self.view.setContextMenuPolicy(Qt.CustomContextMenu);
        self.view.customContextMenuRequested.connect(lambda pt:self.rowsMenu.exec_(self.mapToGlobal(pt)))

        self.selectOnLayersAct=self.rowsMenu.addAction('select on layers')
        self.selectOnLayersAct.setToolTip('select these rows on network and/or readings layers.')
        self.selectOnLayersAct.triggered.connect(self.selectOnLayers)

        self.selectFromLayersAct=self.rowsMenu.addAction('select from layers')
        self.selectFromLayersAct.setToolTip('set selected rows from selected features of readings layer.')
        self.selectFromLayersAct.triggered.connect(self.selectFromLayers)

        self.deleteRowsAct=self.rowsMenu.addAction('delete selected rows')
        self.deleteRowsAct.triggered.connect(self.deleteSelectedRows)

        self.addMenu=self.rowsMenu.addMenu('add new row')
        self.rowAfterAct=self.addMenu.addAction('add empty row after last selected')
        self.rowAfterAct.triggered.connect(self.addEmptyRow)

        self.addFromFeatsAct=self.addMenu.addAction('add new row from selected features')
        self.addFromFeatsAct.triggered.connect(self.addFromFeats)


    def addRow(self):
        pass
        
    
    def selectOnLayers(self):
        pass
        
    def addEmptyRow(self):
        pass
        #self.model.insertEmptyRow(self.lastSelectedRow())
        '''
        ls=self.last_selected_row()
        if not ls:
            ls=0

        d={'run':self.current_run()}
        s_line=self.route_model.index(ls,self.route_model.fieldIndex('e_line')).data()  
        if s_line:
            d.update({'s_line':s_line})

        self.dd.insert_into_routes(d)
        self.route_model.select()
        '''

    def lastSelectedRow(self):
        rows=[r.row() for r in self.routeView.selectionModel().selectedRows()]
        if rows:
            return min(rows)


    def selectFromLayers(self):
        pass
    
    '''
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
'''

    def addFromFeats(self):
        pass
        '''
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
           ''' 
           

    def automakeRun(self):
        self.model.automakeRun(self.currentRun())
        self.model.select()
        iface.messageBar().pushMessage('fitting tool:autofit.')


#might change run_box to subclass with search. May need to use something other than currentText()
    def currentRun(self):
        return self.runBox.currentText()



        
    #def save_route(self):
     #   s=file_dialogs.save_file_dialog('.csv',default_name=self.current_run())
       # if s:
        #    self.dd.download_route(s,self.current_run())


  #  def save_routes(self):
   #     s=file_dialogs.save_file_dialog('.csv',default_name='routes.csv')
   #     if s:
    #        self.dd.download_routes(s)        


#    def upload_routes(self):
 #       files=file_dialogs.load_files_dialog('.csv')
  #      iface.messageBar().pushMessage(str(files))
   #     sucessful=[]
    #    unsucessful=[]
     #   for f in files:
      #      try:
       #         self.dd.upload_route(f)
        #       # upload_routes_csv.upload_route(csv=f,con=self.dd.psycopg2_con())
         #       sucessful.append(f)
#
 #           except Exception as e:
  #              iface.messageBar().pushMessage('fitting tool: error uploading route:%s:%s'%(f,e),duration=5)
               # print 'fitting tool: error uploading route:%s:%s'%(f,e)
   #             unsucessful.append(f)

#        iface.messageBar().pushMessage('fitting tool attempted to upload routes: sucessfull:%s. unsucessfull:%s'%(','.join(sucessful),','.join(unsucessful)))
#        self.route_model.select()


#    def refresh_view(self):
#        self.route_model.select()
#       self.route_view.viewport().update()
        
           

#    def drop_selected_rows(self):
 #       self.drop_rows([r.row() for r in self.route_view.selectionModel().selectedRows()])


    #list of ints
  #  def drop_rows(self,rows):
   #     for row in sorted(rows, reverse=True):#bottom to top because deleting row changes index
    #        self.route_model.removeRow(row)
     #   self.route_model.select()

    
   
        
    #select selected rows of routes table on layers
    '''
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
'''
    
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

        
    


