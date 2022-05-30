# -*- coding: utf-8 -*-
"""
Created on Mon May 16 11:28:36 2022

@author: Drew.Bennett
"""

from PyQt5.QtCore import QModelIndex

from PyQt5.QtSql import QSqlQuery,QSqlQueryModel,QSqlDatabase
import psycopg2

from hsrr_processor.functions import layer_functions
from qgis.core import QgsCoordinateReferenceSystem


'''
read only model for network.
    use for sec_widget and chainage_widget.
    
    needs 1 row per section.

'''


class networkModel(QSqlQueryModel):
    
        
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setLayer(None)
        self.setField(None)
        self.setDb(QSqlDatabase())
        
        
        
    def setDb(self,db):
        
        q = QSqlQuery('select sec from hsrr.network',db)
        self.setQuery(q)
        
        self.db = db
        
        try:
            self.con = psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())   
        except:
            self.con = None

        

    def getCrs(self):
        return QgsCoordinateReferenceSystem(27700)
        

        
    def sectionToRow(self,sec):
        pass
    
    
    
#run query and get result of 1st line
    def singleLineQuery(self, query,args):
        if self.con is not None:        
            cur = self.con.cursor()
            cur.execute(query,args)
            return cur.fetchone()
        
        
    
    #index can be QModelIndex or int with row
   # returns str
    def sec(self,index):
        if isinstance(index,QModelIndex):
            return self.index(index.row(),0).data()
        
        if isinstance(index,int):
            return self.index(index,0).data()   
        
        raise TypeError('networkModel.sec(index) requires QModelIndex or int')
    
    
    
    def indexFromSection(self,sec):
        for r in range(self.rowCount()):
            i = self.index(r,0)
            if i.data()==sec:
                return i          
            
        return self.index(-1,-1)#invalid index
    
    
    
    # x and y to run chainage.
    #returns float
    #index can be QModelIndex or int
    def XYToFloat(self,x,y,index):
        sec = self.sec(index)
        r = self.singleLineQuery("select hsrr.point_to_sec_ch(%(x)s,%(y)s,%(sec)s)",{'x':float(x),'y':float(y),'sec':sec})
        if r is not None:
            return r[0]
        return 0
        
    
    
    # x and y to run chainage.
    #returns float
    #index can be QModelIndex or int
    def XYToChainage(self,x,y,sec):
        r = self.singleLineQuery("select hsrr.point_to_sec_ch(%(x)s,%(y)s,%(sec)s)",{'x':float(x),'y':float(y),'sec':sec})
        if r is not None:
            return r[0]
        return 0
    
    
    
    def chainageToXY(self,chainage,sec):
        r = self.singleLineQuery('select st_x(hsrr.sec_ch_to_point(%(ch)s,%(sec)s)),st_y(hsrr.sec_ch_to_point(%(ch)s,%(sec)s))',{'ch': chainage, 'sec': sec}) 
        if r is not None:
            return r[0]
        return (0,0)
        
        
        
        # run chainage to (x,y) floats
    def floatToXY(self,value,index=None):
        sec = self.sec(index)
        r = self.singleLineQuery('select st_x(hsrr.sec_ch_to_point(%(ch)s,%(sec)s)),st_y(hsrr.sec_ch_to_point(%(ch)s,%(sec)s))',{'ch': value, 'sec': sec})
        if r is None:
            return (0,0)
        else:
            return r
    
    
    
    #returns float
    def maxValue(self,index):
        v = self.secLength(index)
        if v is None:
            return 0
        return v
    
    
    
    def minValue(self,index):
        return 0
    
    
    
    def secLength(self,index):
        r = self.singleLineQuery('select hsrr.meas_len(%(sec)s)',{'sec':self.sec(index)})
        if r is not None:
            return r[0]



    def setLayer(self,layer):
        self._layer = layer
    

    
    def getLayer(self):
        return self._layer
    
    
    
    def setField(self,field):
        self._field = field
        
        
        
    def getField(self):
        return self._field
        
        
        
    def selectedFeatures(self):
        layer = self.getLayer()
        if layer is not None:
            return [f for f in layer.selectedFeatures()]
        return []
        
    
    
    def selectedFeatureRow(self):
        
        network = self.getLayer()
        field = self.getField()
        
        
        if field and (network is not None):
            for f in network.selectedFeatures():
                sec = f[field]
                return self.indexFromSection(sec).row()
            
            
    
    #QModelIndex. invalid index if not found.
    def indexOfSelectedFeature(self):
        
        network = self.getLayer()
        field = self.getField()
        
        if field and (network is not None):
            for f in network.selectedFeatures():
                sec = f[field]
                return self.indexFromSection(sec)
            
        return self.index(-1,-1)#invalid index
            
        
    
    #takes list of rows
    def selectOnLayer(self,rows):
        sections = [self.sec(r) for r in rows]
        self.selectSectionsOnlayer()
            #if sects and sects!=['D']:
              #  layer_functions.zoomToSelected(network)
         
            
              
    def selectSectionsOnlayer(self,sections):
            labField = self.getField()
            network = self.getLayer()
            if labField and network:
                layer_functions.selectOnNetwork(layer=network,labelField=labField,sections=sections)
         
            
         
    
    