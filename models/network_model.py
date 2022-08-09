# -*- coding: utf-8 -*-
"""
Created on Mon May 16 11:28:36 2022

@author: Drew.Bennett



read only model for network.
    use for sec_widget and chainage_widget.
    
    needs 1 row per section.
    
    
    uses connection.getDb() for queries. 
    
    when database connection changed just need to call select()
    
    
    chainage_widget does nothing if x and y not floats. don't need type checkin or defaults here.?'

"""

from PyQt5.QtCore import QModelIndex
from PyQt5.QtSql import QSqlQuery,QSqlQueryModel

from qgis.core import QgsCoordinateReferenceSystem

from hsrr_processor.database import connection

import logging
logger = logging.getLogger(__name__)


import sip


class networkModel(QSqlQueryModel):
    
        
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setLayer(None)
        self.setField(None)
        self.select()


       
    def select(self):
        q = QSqlQuery('select sec from hsrr.network',self.db())
        self.setQuery(q)

        
       
    def db(self):
        return connection.getConnection()
       
        

    def getCrs(self):
        return QgsCoordinateReferenceSystem(27700)
        
    
    
#run query and get result of 1st line
    def runQuery(self, query,args):
        db = self.db()
        
        if db.isOpen():
            q = QSqlQuery(db)
            q.prepare(query)
            
            for k in args:
                q.bindValue(k,args[k])

            q.exec()
            return q
        else:
            logger.warning('database not open')
  
    
    #section from QModelIndex or row(int)
    def sec(self,index):
        if isinstance(index,QModelIndex):
            return self.index(index.row(),0).data()
        
        if isinstance(index,int):
            return self.index(index,0).data()   
        
        raise TypeError('networkModel.sec(index) requires QModelIndex or int')
    
    
    
    #x and y to section chainage.
    #x and y need to be in espg 27700
    def XYToSecCh(self,x,y,sec):
        q = self.runQuery('select hsrr.point_to_sec_ch(:x,:y,:sec)',{':x':x,':y':y,':sec':sec})
        if not q is None:
            if q.next():
                return q.value(0)
        logger.debug('XYtoSecCh returned default.last error:%s',q.lastError().text())
        return 0
        
    
    
    def secChToXY(self,sec,ch):
        
        q = self.runQuery('select st_x(hsrr.sec_ch_to_point(:ch,:sec)),st_y(hsrr.sec_ch_to_point(:ch,:sec))',
                                 {':ch': ch, ':sec': sec})

        if not q is None:
            if q.next():
                if isinstance(q.value(0),float) and isinstance(q.value(1),float):
                    return (q.value(0),q.value(1))
                else:
                    logger.warning('secChToXY query returned non float %s,%s.',q.value(0),q.value(1))

        logger.debug('secChToXY returned default. last error:%s',q.lastError().text())
        return (0,0)
        
    
    #invalid QVariant where result is null.
    #return float. 0 where invalid.
    def secLength(self,sec):
        q = self.runQuery('select hsrr.meas_len(:sec)',{':sec': sec})

        if not q is None:
            if q.next():
                if isinstance(q.value(0),float):
                    return q.value(0)
                else:
                    logger.warning('hsrr.meas_len returned non float %s.',q.value(0))

        logger.debug('secLength returned default. last error:%s',q.lastError().text())
        
        return 0.0
    
    
    
    def indexFromSection(self,sec):
        for r in range(self.rowCount()):
            i = self.index(r,0)
            if i.data()==sec:
                return i                  
        return self.index(-1,-1)#invalid index
    


    def setLayer(self,layer):
        self._layer = layer
    


#layer could be deleted after setting. 
#results in RuntimeError: underlying C/C++ object has been deleted error when trying to use layer
#might be better to avoid storing layer as attribute...
    def layer(self):
        if self._layer is None:
            return None
        
        if sip.isdeleted(self._layer):
            return None

        return self._layer 
            
    
    
    def setField(self,field):
        self._field = field
        
        
        
    def getField(self):
        return self._field
        
        
        
    def selectedFeatures(self):
        layer = self.layer()
        if layer is not None:
            return [f for f in layer.selectedFeatures()]
        return []
        
    
    
    def selectedFeatureRow(self):
        
        network = self.layer()
        field = self.getField()
        
        
        if field and (network is not None):
            for f in network.selectedFeatures():
                sec = f[field]
                return self.indexFromSection(sec).row()
            
            
    
    #QModelIndex. invalid index if not found.
    def indexOfSelectedFeature(self):
        
        network = self.layer()
        field = self.getField()
        
        if field and (network is not None):
            for f in network.selectedFeatures():
                sec = f[field]
                return self.indexFromSection(sec)
            
        return self.index(-1,-1)#invalid index
            


    def selectSectionsOnlayer(self,sections):
            labField = self.getField()
            network = self.layer()
            if labField and network:
               # layer_functions.selectOnNetwork(layer=network,labelField=labField,sections=sections)
                sects = ','.join(["'"+s+"'" for s in sections])
                e = '"{field}" in({sects})'.format(field=labField,sects=sects)
                network.selectByExpression(e)
         
            