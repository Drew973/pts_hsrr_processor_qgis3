# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 11:30:54 2022

@author: Drew.Bennett


undoable_routes_model subclass with methods for selecting on layers and converting chainage to coordinates 
for use with chainage widget.
QGIS dependent.

"""


from hsrr_processor.models.routes.undoable_routes_model import undoableRoutesModel
from hsrr_processor.functions import layer_functions
from qgis.core import QgsCoordinateReferenceSystem



class mainRoutesModel(undoableRoutesModel):
       
    def __init__(self,db,parent=None):
        super().__init__(db=db,parent=parent)
        self.setNetworkModel(None)
        self.setReadingsModel(None)
        
        
        
    def setReadingsModel(self,model):
        self._readingsModel = model
            
        
        
    def readingsModel(self):
        return self._readingsModel
        
    
    
    def setNetworkModel(self,model):
        self._networkModel = model
        
        
        
    def networkModel(self):
        return self._networkModel
        
    
    
    def sec(self,row):
        return self.index(row,self.fieldIndex('sec')).data()



    def sectionLabels(self,rows):
        return [self.sec(r) for r in rows]
    
    
    
    def getCrs(self):
        return QgsCoordinateReferenceSystem(27700)



    def XYToFloat(self,x,y,index):
        c = index.column()
    
        if c == self.fieldIndex('start_sec_ch') or c == self.fieldIndex('end_sec_ch'):
            return self.networkModel().XYToSecCh(x,y,self.sec(index.row()))#x,y,sec
    
        if c == self.fieldIndex('start_run_ch') or c == self.fieldIndex('end_run_ch'):
            return self.readingsModel().XYToChainage(x,y)
    
        return 0
    
    
    
    def floatToXY(self,value,index):
        c = index.column()
    
        if c == self.fieldIndex('start_sec_ch') or c == self.fieldIndex('end_sec_ch'):
            return self.networkModel().secChToXY(ch=value,sec=self.sec(index.row()))
        
        if c==self.fieldIndex('start_run_ch'):
            return self.readingsModel().chainageToXY(value,True)
    
        if c==self.fieldIndex('end_run_ch'):
            return self.readingsModel().chainageToXY(value,False)
    
        return (0,0)



    def minValue(self,index):
        c = index.column()
        if c==self.fieldIndex('start_run_ch') or c==self.fieldIndex('end_run_ch'):
            return self.readingsModel().minValue()
        else:
            return 0
    
    
    
    def maxValue(self,index):
        c = index.column()
        
        if c==self.fieldIndex('start_run_ch') or c==self.fieldIndex('end_run_ch'):
            return self.readingsModel().maxValue()
        
        if c==self.fieldIndex('start_sec_ch') or c==self.fieldIndex('end_sec_ch'):
            sec = index.sibling(index.row(),self.fieldIndex('sec')).data()
            return self.networkModel().secLength(sec)
        
        return 0
        #add sec length here.
    
    
    
    #list of turples [(start,end)] for rows
    def runChainages(self,rows):
        sCol = self.fieldIndex('start_run_ch')
        eCol = self.fieldIndex('end_run_ch')
        return [(self.index(row,sCol).data(),self.index(row,eCol).data()) for row in rows]

    

    def selectOnLayers(self,rows):        
        self.networkModel().selectSectionsOnlayer(self.sectionLabels(rows))
        self.readingsModel().selectOnLayer(self.runChainages(rows))
        layer_functions.zoomToSelectedMultilayer([self.networkModel().layer(),self.readingsModel().layer()])
            
