from PyQt5.QtWidgets import QTableView,QMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence


from hsrr_processor.delegates import sec_delegate,chainage_delegate
from hsrr_processor.models.changesModel import changesModel
from hsrr_processor.models.routes.main_routes_model import mainRoutesModel


import logging
logger = logging.getLogger(__name__)




class changesView(QTableView):
    
    def __init__(self,parent=None,undoStack=None):
        super().__init__(parent)
        self.undoStack = undoStack
        
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
        self.chainageDelegate = chainage_delegate.chainageDelegate(parent=self)



    def setModel(self,model):
        
        logger.debug('setModel(%s)',model)

        super().setModel(model)
        self.resizeColumnsToContents()

        if isinstance(model,changesModel) or isinstance(model,mainRoutesModel):
            
            logger.debug('setModel special')
            
            print(model.fieldIndex('pk'))
            self.hideColumn(model.fieldIndex('pk'))
            
            self.setItemDelegateForColumn(model.fieldIndex('sec'),self.secDelegate)
            
            self.setItemDelegateForColumn(model.fieldIndex('start_run_ch'),self.chainageDelegate)    
            self.setItemDelegateForColumn(model.fieldIndex('end_run_ch'),self.chainageDelegate)
            self.setItemDelegateForColumn(model.fieldIndex('start_sec_ch'),self.chainageDelegate)
            self.setItemDelegateForColumn(model.fieldIndex('end_sec_ch'),self.chainageDelegate)    


        
    #list of row indexes
    def selectedRows(self):
        return [i.row() for i in self.selectionModel().selectedRows()]
    


    def dropSelectedRows(self):
        self.model().dropRows(self.selectedRows())
   
    
                    
    def selectOnLayers(self):
        self.model().selectOnLayers(self.selectedRows())
    

    
    def setNetworkModel(self,model):
        self.secDelegate.setNetworkModel(model)
