# -*- coding: utf-8 -*-
"""
Created on Mon May 16 12:59:43 2022

@author: Drew.Bennett


runs queries on readings table.
selects things on layer.

"""

from PyQt5.QtWidgets import QUndoCommand,QUndoStack
from PyQt5.QtSql import QSqlQuery#QSqlQueryModel


import psycopg2
from qgis.core import QgsCoordinateReferenceSystem
from hsrr_processor.database import connection
from hsrr_processor.models import parse_readings
from hsrr_processor.models import commands,table


import logging
logger = logging.getLogger(__name__)
import sip



class readingsModel:
    
    
    def __init__(self,parent=None):
        #super().__init__(parent)
        self.setRun(None)        
        self.setStartChainageField(None)
        self.setEndChainageField(None)
        self.setLayer(None)
        self.setRunField(None)
        self.setUndoStack(QUndoStack())
        
        
    def database(self):
        return connection.getConnection()
        
        
        
    def setUndoStack(self,undoStack):
        self._undoStack = undoStack
        
        
        
    def undoStack(self):
        return self._undoStack
        
    
    def undo(self):
        self.undoStack().undo()
        
        
        
    def redo(self):
        self.undoStack().redo()
        
        
        
    def getCrs(self):
        return QgsCoordinateReferenceSystem(27700)
    
    
    
    def con(self):
        db = self.database()
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
        layer = self.layer()
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
        logger.debug('setStartChainageField(%s)',field)
        self._startChainageField = field
        
            
        
    def startChainageField(self):
        return self._startChainageField
    
    
        
    def setEndChainageField(self,field):
        logger.debug('setEndChainageField(%s)',field)
        self._endChainageField = field
        

        
    def endChainageField(self):
        return self._endChainageField


        
    def setLayer(self,layer):
        logger.debug('setLayer(%s)',layer)
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

    def setRunField(self,field):
        logger.debug('setRunField(%s)',field)
        self._runField = field



    def runField(self):
        return self._runField
        
    
    #returns float or None
    def minSelected(self):
        field = self.startChainageField()
        layer = self.layer()()
        if field and layer:
            vals = [f[field] for f in layer.selectedFeatures()]
            if len(vals)>0:
                return min(vals)
    
    
    #returns float or None
    def maxSelected(self):
        field = self.endChainageField()
        layer = self.layer()
        if field and layer:
            vals = [f[field] for f in layer.selectedFeatures()]
            if len(vals)>0:
                return max(vals)    
    

    
    #list of (start,end)
    def selectOnLayer(self,chainages):
        sField = self.startChainageField()
        eField = self.endChainageField()
        layer = self.layer()
        run = self.run()
        runField = self.runField()

        if sField and eField and run and runField and layer is not None:
            
            chTemplate = '("{sField}"<{e} and "{eField}">{s})'.format(sField=sField,e='{e}',eField=eField,s='{s}')
            chClause = 'or'.join([chTemplate.format(s=s,e=e) for s,e in chainages])            
            e = '"{runField}"=\'{rn}\' and ({chClause})'.format(runField=runField,rn=run,chClause=chClause)
            logger.debug(e)
            layer.selectByExpression(e)
         
            
                
    def filterLayer(self):
        layer = self.layer()
        run = self.run()
        field = self.runField()
        
        if layer is not None and run is not None and field is not None:
            layer.setSubsetString("%s = '%s'"%(field,run))
        
        
        
    def loadSpreadsheet(self,fileName,run):
        self.undoStack().push(loadCommand(model=self,fileName=fileName))
        
        
        
    #load .xls to run and insert into hsrr.readings. Need to insert run into run_info before calling this.
    def _loadSpreadsheet(self,fileName,run):

        logger.debug('_loadSpreadsheet(%s)'%(fileName))

        with self.con() as con:
            cur = con.cursor()
                
            q = '''
                insert into hsrr.readings(run,f_line,t,raw_ch,rl,vect,s_ch,e_ch)
                values(
                %(run)s
                ,%(f_line)s
                ,to_timestamp(replace(%(t)s,' ',''),'dd/mm/yyyyHH24:MI:ss')
                ,%(raw_ch)s
                ,%(rl)s
                ,ST_MakeLine(St_Transform(ST_SetSRID(ST_makePoint(%(start_lon)s,%(start_lat)s),4326),27700),St_Transform(ST_SetSRID(ST_makePoint(%(end_lon)s,%(end_lat)s),4326),27700))	
                ,%(line)s * 0.1
                ,%(line)s * 0.1 +0.1
                )
            '''
            psycopg2.extras.execute_batch(cur,q,parse_readings.parseReadings(uri=fileName,run=run))
            
            
            
    #takes and returns table(run,file)
    def _addRuns(self,d):
        
        runIndex = d.fieldIndex('run')
        fileIndex=d.fieldIndex('file')
        for r in d.data:
            self._loadSpreadsheet(fileName=r[fileIndex],run=r[runIndex])
            
        return d

        

    def dropRuns(self,runs):
        self.undoStack().push(commands.dropRunsCommand(model=self,runs=runs))
        
    
    #list of runs or table with run column
    def _dropRuns(self,runs):
        
        if isinstance(runs,table.table):
            i = runs.fieldIndex('run')
            runs = [r[i] for r in runs.data]
        
        
        with self.con() as con:
            cur = con.cursor()
            q = 'delete from hsrr.readings where run  = any(%(runs)s) returning pk,run,f_line,t,raw_ch,rl,s_ch,e_ch,st_asText(vect) as vect'
            cur.execute(q,{'runs':runs})
            return {'columns':[desc[0] for desc in cur.description],'data':[r for r in cur.fetchall()]}
    
    
    
    #data like {'columns':[],'data':[()]}
    #wkt can be inserted into geometry column
    #data like{'columns':[],'data':[]}
    def _insert(self,data):
        logger.debug('insert(%s)',data)

        q = 'insert into hsrr.readings({cols}) values {vals} returning pk'.format(cols=','.join(data['columns']),vals='%s')
        
        logger.debug(q)
        logger.debug('data:%s',data['data'])

        with self.con() as c:
            if c is not None:
                cur = c.cursor()
                results = psycopg2.extras.execute_values(cur,q,data['data'],fetch=True)
            
        #return {'columns':['run'],'data':r}
        return [r[0] for r in results]    
        
        
        

class loadCommand(QUndoCommand):
    
    def __init__(self,model,fileName,run,parent=None,description = 'upload run'):
        super().__init__(description,parent)
        self.model = model
        self.fileName = fileName
        self.run = run
        

    def redo(self):
        self.model._loadSpreadsheet(fileName=self.fileName,run=self.run)#{'columns':['run'],'data':[(run)]}
        #generate_run_name is stable. will give same result here.
   


    def undo(self):
        self.model._dropRuns([self.run])

