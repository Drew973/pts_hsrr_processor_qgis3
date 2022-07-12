# -*- coding: utf-8 -*-
"""
Created on Mon May 16 12:59:43 2022

@author: Drew.Bennett



unused.

toDo: merge with readingsModel and run_info_model.


use this for uploading readings instead of seperate function.
need ways to get run chainage and to upload readings.




"""


import psycopg2
from qgis.core import QgsFeatureRequest
from hsrr_processor.functions import layer_functions
from PyQt5.QtSql import QSqlQueryModel,QSqlQuery,QSqlDatabase

from qgis.core import QgsCoordinateReferenceSystem

import logging
logger = logging.getLogger(__name__)

class readingsModel(QSqlQueryModel):
    
    
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setRun(None)
        self.setDb(QSqlDatabase())
        
        self.setStartChainageField(None)
        self.setEndChainageField(None)
        self.setLayer(None)
        self.setRunField(None)
        

        
      
    def setDb(self,db):
        self._db = db
        q = QSqlQuery('select 1',db)#required for index().model() to not be None
        self.setQuery(q)
        
       # try:
       #     self.con = psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())   
       # except:
        #    self.con = None
        
        
    def database(self):
        return self._db
        
        
        
    def getCrs(self):
        return QgsCoordinateReferenceSystem(27700)
    
    
    
    def con(self):
        db = self._db
        try:
            return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())    
        except:
            return None
    
    
#run query and get result of 1st line
    def singleLineQuery(self, query,args):
        c = self.con()
        if c is not None:        
            cur = c.cursor()
            cur.execute(query,args)
            return cur.fetchone()
        
        
    def selectedFeatures(self):
        layer = self.getLayer()
        if layer is not None:
            return [f for f in layer.selectedFeatures()]
        return []
       
        
       
     #(x,y). if first true where multiple points with this chainage return first point in run , otherwise last.
    def chainageToXY(self,chainage,first=True):
        
        q = QSqlQuery(self.database())
        
        if first:
            q.prepare('select st_x(hsrr.run_ch_to_pt_s(:ch,:run)),st_y(hsrr.run_ch_to_pt_s(:ch,:run))')
        else:
            q.prepare('select st_x(hsrr.run_ch_to_pt_e(:ch,:run)),st_y(hsrr.run_ch_to_pt_e(:ch,:run))')

        q.bindValue(':ch',chainage)
        q.bindValue(':run',self._run)

        if q.exec():
            while q.next():
                return (q.value(0),q.value(1))

        else:
            logger.info('query failed')

    
        return (0,0)
        
    
       
    def XYToChainage(self,x,y):
        v = self.singleLineQuery("select hsrr.point_to_run_chainage(%(x)s,%(y)s,%(run)s)",{'x':x,'y':y,'run':self._run})
        if v is not None:
            return v[0]
        return -1
       
        
        
    def maxValue(self,index=None):
        v = self.singleLineQuery('select max(e_ch) from hsrr.readings where run = %(run)s',{'run':self._run})
        if v is not None:
            return v[0]
        return 0
    
    
    
    def minValue(self,index=None):
        v = self.singleLineQuery('select min(s_ch) from hsrr.readings where run = %(run)s',{'run':self._run})
        if v is not None:
            return v[0]
        return 0
        
    

    def setRun(self,run):
        self._run = run
    
    
    
    
    def run(self):
        return self._run
    
        
    def setStartChainageField(self,field):
        self._startChainageField = field
        
            
        
    def getStartChainageField(self):
        return self._startChainageField
    
    
        
    def setEndChainageField(self,field):
        self._endChainageField = field
        

        
    def getEndChainageField(self):
        return self._endChainageField


        
    def setLayer(self,layer):
        self._layer = layer
        
        
        
    def getLayer(self):
        return self._layer

        

    def setRunField(self,field):
        self._runField = field



    def getRunField(self):
        return self._runField
        
    
    #returns float or None
    def minSelected(self):
        field = self.getStartChainageField()
        layer = self.getLayer()
        if field and layer:
            vals = [f[field] for f in layer.selectedFeatures()]
            if len(vals)>0:
                return min(vals)
    
    
    #returns float or None
    def maxSelected(self):
        field = self.getEndChainageField()
        layer = self.getLayer()
        if field and layer:
            vals = [f[field] for f in layer.selectedFeatures()]
            if len(vals)>0:
                return max(vals)    
    
    
    
    def selectOnLayer(self,chainages):
        sField = self.getStartChainageField()
        eField = self.getEndChainageField()
        layer = self.getLayer()
        run = self.run()
        runField = self.getRunField()

        if sField and eField and layer:
            
            if run and runField:
                runFilt = '"{}" = \'{}\' and '.format(runField,run)
            
            else:
                runFilt = ''
            
            
            fids = []
            r = QgsFeatureRequest()
            
            for s,e in chainages:
                
                if e is None:
                    r.setFilterExpression(runFilt+'{eField}>{s}'.format(eField=eField,s=s))#want where ranges overlap

                else:
                    r.setFilterExpression(runFilt+'"{sField}"<{e} and {eField}>{s}'.format(sField=sField,e=e,eField=eField,s=s))#want where ranges overlap
                
                
                for f in layer.getFeatures(r):
                    fids.append(f.id())
            
            
            layer.selectByIds(fids)
            if fids:
                layer_functions.zoomToSelected(layer)
        
        
        
                
    def filterLayer(self):
        layer = self.getLayer()
        run = self.run()
        field = self.getRunField()
        
        if layer is not None and run is not None and field is not None:
            layer.setSubsetString("%s = '%s'"%(field,run))
        