from PyQt5.QtWidgets import QTableView,QMenu
from PyQt5.QtSql import QSqlRelation
from PyQt5.QtCore import Qt


from hsrr_processor.models import changesModel,undoableTableModel
from hsrr_processor import delegates
from hsrr_processor import layerFunctions

#from ..models import changesModel,undoableTableModel
#from .. import delegates
#from .. import layerFunctions



class changesView(QTableView):
    
    def __init__(self,parent=None,undoStack=None,fieldsWidget=None):
        super().__init__(parent)
        self.undoStack = undoStack
        self.fw = fieldsWidget
        
        self.rowsMenu = QMenu(self)
        self.rowsMenu.setToolTipsVisible(True)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu);
        self.customContextMenuRequested.connect(lambda pt:self.rowsMenu.exec_(self.mapToGlobal(pt)))         

        self.selectOnLayers_act = self.rowsMenu.addAction('select on layers')
        self.selectOnLayers_act.setToolTip('select these rows on network and/or readings layers.')
        self.selectOnLayers_act.triggered.connect(self.selectOnLayers)

        #selectFromLayersAct = self.rows_menu.addAction('select from layers')
        #selectFromLayersAct.setToolTip('set selected rows from selected features of readings layer.')
  #      self.select_from_layers_act.triggered.connect(self.select_from_layers)

        self.deleteRowsAct = self.rowsMenu.addAction('delete selected rows')
        self.deleteRowsAct.triggered.connect(self.dropSelectedRows)
        
        
    #connect to database and set model
    
    
    def setDb(self,db):    
        m = changesModel.changesModel(parent=self,db=db,undoStack=self.undoStack)
        m.setRelation(m.fieldIndex('sec'),QSqlRelation('hsrr.network', 'sec', 'sec'))
        
        self.setModel(m)
        [self.setColumnHidden(col, True) for col in m.hiddenColIndexes]#hide run column
        self.resizeColumnsToContents()
        secCol = m.fieldIndex('sec')
        self.setItemDelegateForColumn(secCol,delegates.secWidgetDelegate(parent=self,fw=self.fw,model=m,column=secCol))

        self.setItemDelegateForColumn(m.fieldIndex('ch'),delegates.chainageWidgetDelegate(parent=self,fw=self.fw))     
 
        self.setItemDelegateForColumn(m.fieldIndex('sec'),delegates.searchableRelationalDelegate(self))
        
        
    #first index of selected rows
    def selectedRows(self):
        inds = self.selectionModel().selectedRows()
        if inds:
            return inds
      #  iface.messageBar().pushMessage('hsrr tool:no rows selected')    


    def dropSelectedRows(self):
        
        pkCol = self.model().fieldIndex('pk')
        pks = [{'pk':r.sibling(r.row(),pkCol).data()} for r in self.selectionModel().selectedRows()]
        self.undoStack.push(undoableTableModel.deleteDictsCommand(self.model(),pks,'drop selected rows'))
    
        
        
    #select selected rows of routes table on layers
    def selectOnLayers(self):

        inds = self.selectedRows()
        
        if inds:
            
            #select on network
            secCol = self.model().fieldIndex('sec')
            sects = [i.sibling(i.row(),secCol).data() for i in inds]
            sects = [s for s in sects if not s=='']
            
            networkLayer = self.fw['network']
            secField = self.fw['label']
            
            if networkLayer and secField:
                layerFunctions.selectByVals(sects, networkLayer, secField)
                layerFunctions.zoomToSelected(networkLayer)
       
            
           #select on readings        
            readingsLayer = self.fw['readings']
            s_chField = self.fw['s_ch']
            e_ch_Field = self.fw['e_ch']
            runField = self.fw['run']
            
            ch_field = self.model().fieldIndex('ch')
            
            if readingsLayer and s_chField and e_ch_Field:
                
                fids = []
                for i in inds:                    
                    
                    s = i.sibling(i.row(),ch_field).data()
                    
                    if i.row()<i.model().rowCount()-1:#0 indexed
                        e = i.sibling(i.row()+1,ch_field).data()
                        fids+=layerFunctions.readingsFids(readingsLayer,self.model().run,runField,s,s_chField,e,e_ch_Field)
                    
                    else:
                        fids+=layerFunctions.readingsFids2(layer=readingsLayer,run=self.model().run,runField=runField,ch=s,e_chField=e_ch_Field)
                        
            
                readingsLayer.selectByIds(fids)  
        
                #only want to zoom to these if no section selected
                if not sects:
                    layerFunctions.zoomToSelected(readingsLayer)