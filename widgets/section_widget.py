# -*- coding: utf-8 -*-
"""
Created on Thu May 12 12:58:23 2022

@author: Drew.Bennett
"""


#from hsrr_processor.widgets import searchable_combo_box
#from hsrr_processor.functions import layer_functions

from PyQt5.QtWidgets import QAction,QComboBox


class sectionWidget(QComboBox):
    
    
    
    def __init__(self,parent=None):
        super().__init__(parent)
        self.selectAct = QAction('Select on layer',self)
        self.selectAct.triggered.connect(self.selectOnLayer)
        self.setFromLayerAct = QAction('Set from layer',self)
        self.setFromLayerAct.triggered.connect(self.setFromLayer)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert) 
        
        
        
    def setValue(self,value):
       # i = self.findData(value)#-1 for everything. role?
        
        i = self.findText(value)
      
        #print('row:',i,'value:',value)
        
        if i !=-1:
            self.setCurrentIndex(i)
        
        
        
    def contextMenuEvent(self,event):
        menu = self.lineEdit().createStandardContextMenu()
        menu.addAction(self.selectAct)
        menu.addAction(self.setFromLayerAct)
        menu.exec(event.globalPos())
        
        
        
    def selectOnLayer(self):
        self.model().selectOnLayer(rows=[self.currentIndex()])


    
    #set value of widget from layer
    def setFromLayer(self):
        r = self.model().selectedFeatureRow()
        if r is not None:
            self.setCurrentIndex(r)
   
    