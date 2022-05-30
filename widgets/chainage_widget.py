# -*- coding: utf-8 -*-
"""
Created on Fri May 13 08:40:35 2022

@author: Drew.Bennett



QDoubleSpinBox with:
    option to display marker on map
    set value from map click



needs model to map double to point. with:

    XYToFloat(index,x,y) method
    point is in self.crs
    
    floatToXY(index,value) method. returns (x,y) in model crs
    floatToXY

"""

from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtCore import QModelIndex


from qgis.gui import QgsMapToolEmitPoint,QgsVertexMarker
from qgis.utils import iface
from qgis.core import QgsPointXY, QgsCoordinateTransform, Qgis, QgsProject



class chainageWidget(QDoubleSpinBox):
    
    
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setIndex(QModelIndex())
        self.tool = QgsMapToolEmitPoint(iface.mapCanvas())
       # self.tool = chainageEmitter()
        
        self.marker = QgsVertexMarker(iface.mapCanvas())
        self.marker.setIconSize(20)
        self.marker.setPenWidth(5)
        self.tool.canvasClicked.connect(self.setFromPoint)
    
        self.valueChanged.connect(self.updateMarker)       
        
    
        self.setSingleStep(0.01)
        self.setDecimals(3)
        self.updateMarker(self.value())

    
    '''
    set index (QModelIndex).
    index and it's model is used to convert between points and values
    need index in networkModel for section chainage as depends on section.
    any index for run_chainage as only need run and value.
    '''
    
    def setIndex(self,index):
        self._index = index
        
        if index.model() is not None:
            self.setMinimum(index.model().minValue(index))
            self.setMaximum(index.model().maxValue(index))
            self.updateMarker(self.value())

        

    def getIndex(self):
        return self._index
            
        
    
    def setCrs(self,crs):
        self._crs = crs
    
    
    
    def getCrs(self):
        return self._crs
    
    
    
    #transform from project crs to self.crs
    def getTransform(self):
        m = self.getIndex().model()
        if m is not None:
            crs = m.getCrs()
            if crs is not None:
                return QgsCoordinateTransform(QgsProject.instance().crs(),crs,QgsProject.instance())
    
    
    
    #happens after focusOutEvent
    def setFromPoint(self,point):
        
        print('chainageWidget.setFrompoint')
        
        index = self.getIndex()
        
        print('index:',index)
        m = index.model()
        
        if m is not None:
            print('point:',point)
            pt = self.getTransform().transform(point)
            
            v = m.XYToFloat(pt.x(),pt.y(),index)
            
            print(v)
            
            if isinstance(v,float):
                self.setValue(v)
            
        

    def updateMarker(self,val):
        i = self.getIndex()
        
        m = i.model()
       
        if m is not None:
            
            x,y = m.floatToXY(val,i)
            
            if not (x is None or y is None):
                pt = QgsPointXY(x,y)
                pt = self.getTransform().transform(pt,Qgis.TransformDirection.Reverse)#convert to project crs
                self.marker.setCenter(pt)#needs to be in project crs



    def focusInEvent(self,event):
        iface.mapCanvas().setMapTool(self.tool)
        self.marker.show()
        super().focusInEvent(event)

    

    #happens before setFromPoint and before delegate destroys widget
    def focusOutEvent(self,event):
       # print(type(event))
        
        #iface.mapCanvas().unsetMapTool(self.tool)
#        print('chainage widget.focusOutEvent')
        self.marker.hide()
        super().focusOutEvent(event)
        