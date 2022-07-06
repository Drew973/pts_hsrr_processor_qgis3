# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 10:40:08 2022

@author: Drew.Bennett
"""


from PyQt5.QtWidgets import QTableView,QMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence

from hsrr_processor.functions import layer_functions



class coverageView(QTableView):
    
    def __init__(self,parent=None,undoStack=None,fieldsWidget=None):
        super().__init__(parent)
       
        
        self.rowsMenu = QMenu(self)
        self.rowsMenu.setToolTipsVisible(True)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu);
        self.customContextMenuRequested.connect(lambda pt:self.rowsMenu.exec_(self.mapToGlobal(pt)))         

        self.selectOnLayersAct = self.rowsMenu.addAction('select on network layer')
        self.selectOnLayersAct.setShortcut(QKeySequence('Alt+1'))#focus policy of dockwidget probably important here
        self.selectOnLayersAct.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.selectOnLayersAct.setToolTip('select these rows on network layer.')
        self.selectOnLayersAct.triggered.connect(self.selectOnLayers)
        self.addAction(self.selectOnLayersAct)#qmenu doesnt recieve keypress event if not open?


     
    def setModel(self,model):
        super().setModel(model)
        
        

    #list of row indexes
    def selectedRows(self):
        return [i.row() for i in self.selectionModel().selectedRows()]
    

                    
    def selectOnLayers(self):
        
        m = self.networkModel()
        if m is not None:
        
            sections = self.model().sectionLabels(self.selectedRows())
            m.selectSectionsOnlayer(sections)
            layer_functions.zoomToFeatures(m.selectedFeatures())
        
        
        
    def networkModel(self):
        return self._networkModel
        
    
    
    def setNetworkModel(self,model):
        self._networkModel = model
