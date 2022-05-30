# -*- coding: utf-8 -*-
"""
Created on Mon May 16 11:54:48 2022

	xsp
	ch
	start_sec_ch
	end_sec_ch


@author: Drew.Bennett


copy Routes View with qsortfilterproxymodel with single row? 
    model.setFilterKeyColumn(1) with pk col.
    
    add pk method to source model
    




"""
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QDialogButtonBox,QDialog,QGridLayout,QLabel


from hsrr_processor.widgets import section_widget,chainage_widget


class addRowDialog(QDialog):
    
    
    def __init__(self,parent=None):
        super().__init__(parent)
        
        self.setLayout(QGridLayout(self))
        
        self.secWidget = section_widget.sectionWidget(self)
        self.secWidget.setToolTip('Section Label')
        self.addWidget(self.secWidget,'Section Label')#row,col
        
        self.runChWidget = chainage_widget.chainageWidget(parent=self)
        self.runChWidget.setToolTip('Run chainage.')
        self.addWidget(self.runChWidget,'Run Chainage')

        self.startSecChWidget = chainage_widget.chainageWidget(parent=self)
        self.addWidget(self.startSecChWidget,'Start Section chainage')
        self.runChWidget.setToolTip('Run chainage.')

        
        self.endSecChWidget = chainage_widget.chainageWidget(parent=self)
        self.addWidget(self.endSecChWidget,'End Section Chainage')      
        
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.rejected.connect(self.reject)
        self.buttons.accepted.connect(self.accept)
        
        self.layout().addWidget(self.buttons,3,0,1,3)#row,col,rowspan,colspan
        
        self.secWidget.currentIndexChanged.connect(self.networkIndexSet)
        
        
        
    def addWidget(self,widget,label=''):
        #empty QGridLayout has 1 column
        if self.layout().count()==0:
            col = 0
        else:
            col = self.layout().columnCount()
            
        self.layout().addWidget(QLabel(text = label, parent = self) , 0, col)#row,col
        self.layout().addWidget(widget,1,col,Qt.AlignLeft)#row,col
        
        
        
    def setNetworkModel(self,model):
        #self._networkModel = model
        self.secWidget.setModel(model)
        self.networkFromSelected()


    
    def setReadingsModel(self,model):
        #self._readingsModel = model
        self.runChWidget.setIndex(model.index(0,0))
        self.readingsFromSelected()
            
        
            
    def sec(self):
        return self.secWidget.itemText(self.secWidget.currentIndex())
            
            
            
    def accept(self):
      
        self._routeModel.insertRow(sec = self.sec(),
                                           xsp = None,
                                           ch = self.runChWidget.value(),
                                           note = None,
                                           startSecCh = self.startSecChWidget.value(),
                                           endSecCh = self.endSecChWidget.value()
                                           )
        super().accept()
            
        
            
    def setRouteModel(self,model):
        self._routeModel = model
            
            
          
    def getNetworkModel(self):
        return self.secWidget.model()
        
        
        
    def getReadingsModel(self):
        return self.runChWidget.getIndex().model()
        
        
          
    def networkFromSelected(self):
        m = self.getNetworkModel()
        i = m.indexOfSelectedFeature()
        self.secWidget.setCurrentIndex(i.row())
        self.networkIndexSet(i.row())
        
        
        
    def networkIndexSet(self,row):
        i = self.getNetworkModel().index(row,0)
        self.startSecChWidget.setIndex(i)
        self.endSecChWidget.setIndex(i)
          
        v = self.getNetworkModel().maxValue(i)
        if v is not None:
            self.endSecChWidget.setValue(v)
            
            
            
    def readingsFromSelected(self):
        m = self.getReadingsModel()
        if m is not None:
            v = m.minSelected()
            if v is not None:
                self.runChWidget.setValue(v)