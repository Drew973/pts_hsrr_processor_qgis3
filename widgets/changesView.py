from PyQt5.QtWidgets import QTableView,QMenu,QDoubleSpinBox,QComboBox
from PyQt5.QtSql import QSqlRelation
from PyQt5.QtCore import Qt


from hsrr_processor.models import changesModel,undoableTableModel
from hsrr_processor import delegates
from hsrr_processor.widgets import layerFunctions,dict_dialog
#from ..models import changesModel,undoableTableModel
#from .. import delegates
#from .. import layerFunctions
import logging
logger = logging.getLogger(__name__)


class changesView(QTableView):
    
    def __init__(self,parent=None,undoStack=None,fieldsWidget=None):
        super().__init__(parent)
        self.undoStack = undoStack
        self.fw = fieldsWidget
        
        
        #set xsp dialog
        self.setXspDialog = dict_dialog.dictDialog(parent=self)
        w = QComboBox(self.setXspDialog)
        w.addItems(['CL1','CL2','CR1','CR2','LE','RE'])
        self.setXspDialog.addWidget('xsp',w,True)
        self.setXspDialog.accepted.connect(self.setXsp)  
                
        
        #add row dialog        
        self.addRowDialog = dict_dialog.dictDialog(parent=self)
        w = QDoubleSpinBox(self.addRowDialog)
        w.setSingleStep(0.1)
        self.addRowDialog.addWidget('ch',w,True)
        self.addRowDialog.accepted.connect(self.addRow)
        
        
        #rows menu
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
        
        
        #top menu
        self.fittingMenu = QMenu('Fitting')
        setXspAct = self.fittingMenu.addAction('Set xsp of run...')
        setXspAct.triggered.connect(self.setXspDialog.show)
        
        self.addRowAct = self.fittingMenu.addAction('Add row...')
        self.addRowAct.triggered.connect(self.showAddDialog)
        
        
        autofitMenu = self.fittingMenu.addMenu('Autofit')
        topoAutofitAct = autofitMenu.addAction('Topology based')
        topoAutofitAct.triggered.connect(self.topoAutofit)
        self.fittingMenu.setEnabled(False)

        
        
    #connect to database and set model
    
    
    def setDb(self,db):    
        m = changesModel.changesModel(parent=self,db=db,undoStack=self.undoStack)
        
        if db.isOpen():
            self.fittingMenu.setEnabled(True)        
        
            m.setRelation(m.fieldIndex('sec'),QSqlRelation('hsrr.network', 'sec', 'sec'))
            
            self.setModel(m)
            [self.setColumnHidden(col, True) for col in m.hiddenColIndexes]#hide run column
            self.resizeColumnsToContents()
            secCol = m.fieldIndex('sec')
            self.setItemDelegateForColumn(secCol,delegates.secWidgetDelegate(parent=self,fw=self.fw,model=m,column=secCol))
    
            self.setItemDelegateForColumn(m.fieldIndex('ch'),delegates.chainageWidgetDelegate(parent=self,fw=self.fw))     
     
            self.setItemDelegateForColumn(m.fieldIndex('sec'),delegates.searchableRelationalDelegate(self))

        else:
            self.fittingMenu.setEnabled(False)

        

    def setRun(self,run):
        self.model().setRun(run)
        if run:
            self.fittingMenu.setEnabled(True)
        
        
    #first index of selected rows
    def selectedRows(self):
        inds = self.selectionModel().selectedRows()
        if inds:
            return inds
      #  iface.messageBar().pushMessage('hsrr tool:no rows selected')    


    def topoAutofit(self):
        m = self.model()
        if m.run:
            self.undoStack.push(changesModel.methodCommand(m.topologyAutofit,None,m.deleteDicts,'topology based autofit'))
            

    def setXsp(self):
        self.undoStack.push(self.model().setXspCommand(self.setXspDialog['xsp']))


    def showAddDialog(self):
        if self.model().run:
            self.addRowDialog.widget('ch').setValue(self.fw.lowestSelectedReading(self.currentRun()))
            self.addRowDialog.show()
    
    
    def addRow(self):
        data = [{'run':self.currentRun(),'sec':'','reversed':None,'xsp':None,'ch':self.addRowDialog['ch'],'note':None,'start_sec_ch':None,'end_sec_ch':None}]
        self.undoStack.push(undoableTableModel.insertDictsCommand(self.changesView.model(),data,'add row'))
        
        
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
            
            self.fw.selectOnNetwork(sects)
            
           #select on readings        
            readingsLayer = self.fw['readings']
            

            runFieldIndex = self.model().fieldIndex('run')
            chField = self.model().fieldIndex('ch')
            
            
            #[[run,s_ch,e_ch]]            
            def rse(model,row):
                return [model.index(row,runFieldIndex).data(),model.index(row,chField).data(),model.index(row+1,chField).data()]#None if outside rowcount
            
            
            #want to select features with s_ch > changes.ch for last feature.            
            self.fw.selectOnReadings([rse(self.model(),i.row()) for i in inds])
            #only want to zoom to these if no section selected
            if not sects:
                layerFunctions.zoomToSelected(readingsLayer)
                    
                    

        