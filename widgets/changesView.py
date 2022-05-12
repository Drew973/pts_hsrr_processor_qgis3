from PyQt5.QtWidgets import QTableView,QMenu

from PyQt5.QtCore import Qt
from qgis.core import QgsFeatureRequest



from hsrr_processor.models import changesModel,undoableTableModel
from hsrr_processor import delegates
from hsrr_processor import layerFunctions

#from ..models import changesModel,undoableTableModel
#from .. import delegates
#from hsrr_processor import layerFunctions



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
        
        self.setModel(m)
        [self.setColumnHidden(col, True) for col in m.hiddenColIndexes]#hide run column
        self.resizeColumnsToContents()
        secCol = m.fieldIndex('sec')
        self.setItemDelegateForColumn(secCol,delegates.secWidgetDelegate(parent=self,fw=self.fw,model=m,column=secCol))

        self.setItemDelegateForColumn(m.fieldIndex('ch'),delegates.chainageWidgetDelegate(parent=self,fw=self.fw))     
 
        self.setItemDelegateForColumn(m.fieldIndex('sec'),delegates.searchableRelationalDelegate(self))
        
        
    #list of row indexes
    def selectedRows(self):
        return [i.row() for i in self.selectionModel().selectedRows()]
    


    def dropSelectedRows(self):
        pkCol = self.model().fieldIndex('pk')
        pks = [{'pk':r.sibling(r.row(),pkCol).data()} for r in self.selectionModel().selectedRows()]
        self.undoStack.push(undoableTableModel.deleteDictsCommand(self.model(),pks,'drop selected rows'))
    
    
    
    def getNetworkLayer(self):
        return self.fw['network']
     
        
     
    def getLabelField(self):
        return self.fw['label']
   
    
   
    def getReadingsLayer(self):
        return self.fw['readings']
    
    
    
    def getRunStartChainageField(self):
        return self.fw['s_ch']



    def getRunEndChainageField(self):
       return self.fw['e_ch']    
    
    
    
    def getRun(self):
        return self.model().run
    
    

    def getRunField(self):
        return self.fw['run']
        
        
    
#select selected rows on network layer
    def selectOnNetwork(self):
        labField = self.getLabelField()
        network = self.getNetworkLayer()
        if labField and network:
            sects = self.model().sectionLabels(self.selectedRows())
            layerFunctions.selectByVals(sects,network,labField)
            layerFunctions.zoomToSelected(network)
            
            
            
    def selectOnReadings(self):
        sField = self.getRunStartChainageField()
        eField = self.getRunEndChainageField()
        layer = self.getReadingsLayer()
        run = self.getRun()
        runField = self.getRunField()

        if sField and eField and layer:
            
            if run and runField:
                runFilt = '"{}" = \'{}\' and '.format(runField,run)
            
            else:
                runFilt = ''
            
            chainages = self.model().runChainages(self.selectedRows())#only includes current run
            fids = []
            r = QgsFeatureRequest()
            
            for s,e in chainages:
                
                if e is None:
                    r.setFilterExpression(runFilt+'{eField}>{s}'.format(eField=eField,s=s))#want where ranges overlap

                else:
                    r.setFilterExpression(runFilt+'"{sField}"<={e} and {eField}>{s}'.format(sField=sField,e=e,eField=eField,s=s))#want where ranges overlap
                
                print(r.filterExpression())
                
                for f in layer.getFeatures(r):
                    fids.append(f.id())
            
            
            layer.selectByIds(fids)
            if fids:
                layerFunctions.zoomToSelected(layer)

                    
                    
    def selectOnLayers(self):
        self.selectOnNetwork()
        self.selectOnReadings()