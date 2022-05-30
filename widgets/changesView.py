from PyQt5.QtWidgets import QTableView,QMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence


from hsrr_processor.delegates import sec_delegate,chainage_delegate



class changesView(QTableView):
    
    def __init__(self,parent=None,undoStack=None,fieldsWidget=None):
        super().__init__(parent)
        self.undoStack = undoStack
        self.fw = fieldsWidget
        
        self.rowsMenu = QMenu(self)
        self.rowsMenu.setToolTipsVisible(True)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu);
        self.customContextMenuRequested.connect(lambda pt:self.rowsMenu.exec_(self.mapToGlobal(pt)))         


        self.selectOnLayersAct = self.rowsMenu.addAction('select on layers')
        self.selectOnLayersAct.setShortcut(QKeySequence('Alt+1'))#focus policy of dockwidget probably important here
       
        self.selectOnLayersAct.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.addAction(self.selectOnLayersAct)#qmenu doesnt recieve keypress event if not open?

        self.selectOnLayersAct.setToolTip('select these rows on network and/or readings layers.')
        self.selectOnLayersAct.triggered.connect(self.selectOnLayers)

        #selectFromLayersAct = self.rows_menu.addAction('select from layers')
        #selectFromLayersAct.setToolTip('set selected rows from selected features of readings layer.')
  #      self.select_from_layers_act.triggered.connect(self.select_from_layers)

        self.deleteRowsAct = self.rowsMenu.addAction('delete selected rows')
        self.deleteRowsAct.triggered.connect(self.dropSelectedRows)
        
        #create delegates
        self.secDelegate = sec_delegate.secDelegate(self)
        self.startSecChainageDelegate = chainage_delegate.sectionChainageDelegate(parent=self)
        self.endSecChainageDelegate = chainage_delegate.sectionChainageDelegate(parent=self)
        self.runChDelegate = chainage_delegate.runChainageDelegate(parent=self)



    def setChangesModel(self,model):
        self.setModel(model)
        [self.setColumnHidden(col, True) for col in model.hiddenColIndexes]#hide run column
        self.resizeColumnsToContents()

        
        self.setItemDelegateForColumn(model.fieldIndex('sec'),self.secDelegate)
        self.setItemDelegateForColumn(model.fieldIndex('ch'),self.runChDelegate)    
        self.setItemDelegateForColumn(model.fieldIndex('start_sec_ch'),self.startSecChainageDelegate)
        self.setItemDelegateForColumn(model.fieldIndex('end_sec_ch'),self.endSecChainageDelegate)

        

        
    #list of row indexes
    def selectedRows(self):
        return [i.row() for i in self.selectionModel().selectedRows()]
    


    def dropSelectedRows(self):
        self.model().dropRows(self.selectedRows())
   
    
   
    def setReadingsModel(self,model):
        self._readingsModel = model
        self.runChDelegate.setModel(model)
    
    
   
    def getReadingsModel(self):
        return self._readingsModel
   
    
                    
    def selectOnLayers(self):
        self.model().selectOnLayers(self.selectedRows())
    
        
        
    def getNetworkModel(self):
        return self._networkModel
        
    
    
    def setNetworkModel(self,model):
        self._networkModel = model
        self.secDelegate.setNetworkModel(self._networkModel)
        self.startSecChainageDelegate.setModel(model)
        self.endSecChainageDelegate.setModel(model)