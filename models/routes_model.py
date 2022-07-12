# -*- coding: utf-8 -*-
"""
Created on Fri Jul  8 15:30:34 2022

@author: Drew.Bennett
"""

from PyQt5.QtSql import QSqlTableModel
from qgis.core import QgsCoordinateReferenceSystem

import logging
logger = logging.getLogger(__name__)


import psycopg2
import psycopg2.extras#not always imported with import psycopyg2. version dependent.


#from hsrr_processor.undo_commands.commands import multiUpdateCommand,pairedFunctionCommand,functionCommand
from hsrr_processor.functions import layer_functions


from hsrr_processor.models.undoable_table_model.undoable_table_model import undoableTableModel



'''
QSqlTable model based.
database independent and can be cached.
very buggy.
concurency?




    model with routes table.
    undoable:
        -setData/update
        -insert
        -drop
        -dropRuns(insert is inverse)
        -setXsp (could do directly through update query or loop though setData.)
        -autofit(drop rows is inverse)
    
    
    run various queries for chainage widget
    XYToFloat
    floatToXy
    minValue
    maxValue
    
    
    {columns:[],'data':[[]]}
    can get columns through  [desc[0] for desc in cur.description]

    
    
    
    select on layers.
        do through networkModel and readingsModel.
    
    
    runQuery(query,args) definitly useful
    
    possibility of multiple users means want something like refresh on field change
    
    
    
    editable QSqlQuery may be easiest.
    know what happens when multiple users acess same database
    update(pk,columns,data)
    
    
    
    
    
    
    
'''


class routesModel(undoableTableModel):

    
#db=qsqldatabase
    def __init__(self,db,parent=None):
        super().__init__(parent=parent,db=db)
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
       
        self.setTable('hsrr.routes')
        self.hiddenColIndexes = [self.fieldIndex(col) for col in ['run','pk']]#needs to be after setTable

        self.setRun('')


    def fieldName(self,column):
        return self.record().fieldName(column)
        


    def getCrs(self):
        return QgsCoordinateReferenceSystem(27700)



    def con(self):
        db = self.database()
        try:
            return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())   
        except:
            return None



    def setRun(self,run):
        self._run = run
        f = "run = '{run}' order by start_run_ch, NULLIF( sec,'D') NULLS FIRST".format(run=run)#start_run_ch,dummys,other sections
        self.setFilter(f)
        self.select()
   


    def run(self):
        return self._run

        
        
    def setReadingsModel(self,model):
        self._readingsModel = model
        
        
    
    def XYToFloat(self,x,y,index):
        c = index.column()
    
        if c == self.fieldIndex('start_sec_ch') or c == self.fieldIndex('end_sec_ch'):
            return self._networkModel.XYToChainage(x,y,self.sectionLabel(index))#x,y,sec
    
        if c == self.fieldIndex('ch') or c == self.fieldIndex('e_ch'):
            return self._readingsModel.XYToChainage(x,y)
    
        return 0
    
    
    
    
    def floatToXY(self,value,index):
        c = index.column()
    
        if c == self.fieldIndex('start_sec_ch') or c == self.fieldIndex('end_sec_ch'):
            return self._networkModel.chainageToXY(value,self.sectionLabel(index))#x,y,sec
        
        if c==self.fieldIndex('start_run_ch'):
            return self._readingsModel.chainageToXY(value,True)
    
        if c==self.fieldIndex('end_run_ch'):
            return self._readingsModel.chainageToXY(value,False)
    

        return (0,0)


    def minValue(self,index):
        c = index.column()
        if c==self.fieldIndex('start_run_ch') or c==self.fieldIndex('end_run_ch'):
            return self._readingsModel.minValue()
        
        if c==self.fieldIndex('start_sec_ch') or c==self.fieldIndex('end_sec_ch'):#same effect but more explicit.
            return 0
        
        return 0
    
    
    def maxValue(self,index):
        c = index.column()
     
        if c==self.fieldIndex('start_run_ch') or c==self.fieldIndex('end_run_ch'):
            return self._readingsModel.maxValue()
        
        if c==self.fieldIndex('start_sec_ch') or c==self.fieldIndex('end_sec_ch'):
            sec = index.sibling(0,self.fieldIndex('sec')).data()
            return self.networkModel().measLen(sec)
        
        return 0
   
    
    def setNetworkModel(self,model):
        self._networkModel = model
    
    
    
    def networkModel(self):
        return self._networkModel
    
    
    
    def dropRuns(self,runs):
        pass
       # self.undoStack.push(commands.dropRunsCommand(model=self,runs=runs))  
        
        
    
    #remove runs from routes table and return deleted data.
    def _dropRuns(self,runs):
        with self.con() as con:
            cur = con.cursor()
            cur.execute('delete from hsrr.routes where run = any(%(runs)s) returning run,start_run_ch,end_run_ch,note,sec,start_sec_ch,end_sec_ch,xsp,pk',{'runs':runs})
            
            if self.run() in runs:
                self.setRun(None)            
            
            return [r for r in cur.fetchall()]

##########

    def addRow(self,run=None,startRunCh=None,endRunCh=None,note=None,sec=None,startSecCh=None,endSecCh=None,xsp=None,pk=None):
        
        if not run:
            run = self.run()
        
        args = {'run':run,'start_run_ch':startRunCh,'end_run_ch':endRunCh,'note':note,'sec':sec,'start_sec_sch':startSecCh,'end_sec_ch':endSecCh,'xsp':xsp,'pk':pk}
        
        logger.debug('insertRow:%s',args)
        print(args)
      #  rec = self.record()
        
      #  for i in reversed(range(rec.count())):#count down because removing field will change following field indexes.
     #       if rec.fieldName(i) in args:
      #          if args[rec.fieldName(i)] is None:
     #               rec.remove(i)
     #       else:
     #           rec.remove(i)
  
       # self.insertRecords([rec])
        super().insertRow(**args)
        self.select()
    

    #autofit run, returning primary keys of new rows
    def topologyAutofit(self,arg=None):
        logger.info('topologyAutofit(),run %s'%(self.run))
        if not self.run is None:
            with self.con() as con:
                cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute('select pk from hsrr.topology_based_autofit(%(run)s)',{'run':self.run})
                res = [dict(r) for r in cur.fetchall()]
            self.select()
            return res



    def runQuery(self,query,args):
        con = self.con()
        if con is not None:
            cur = con.cursor()
            cur.execute(query,args)
            r = [r for r in cur.fetchall()]
            con.commit()
            return r



    def sequencialScoreAutofit(self):
        pass
        #self.undoStack.push(pairedFunctionCommand(function = self._sequencialScoreAutofit,inverseFunction=self._dropRows,description='sequencialScoreAutofit'))



    def simpleAutofit(self):
        pass
        #self.undoStack.push(pairedFunctionCommand(function = self._simpleAutofit,inverseFunction=self._dropRows,description='sequencialScoreAutofit'))



    def filteredAutofit(self):
        pass
        #self.undoStack.push(pairedFunctionCommand(function = self._filteredAutofit,inverseFunction=self._dropRows,description='filteredAutofit'))



    def _filteredAutofit(self):
        if self.run is not None:
           r = {'pks':self.runQuery('select pk from hsrr.filtered_autofit(%(run)s)', {'run': self.run()})}
           self.select()
           return r
       
        

    def _simpleAutofit(self):
      #  print('_sequencialScoreAutofit',self.run)
        if self.run is not None:
           r = {'pks':self.runQuery('select pk from hsrr.simple_autofit(%(run)s)', {'run': self.run()})}
           self.select()
           return r
        
        

    def _sequencialScoreAutofit(self):
      #  print('_sequencialScoreAutofit',self.run)
        if self.run is not None:
           r = {'pks':self.runQuery('select pk from hsrr.filtered_autofit(%(run)s)', {'run': self.run()})}
           self.select()
           return r
   
    
    def leastCostAutofit(self):
        pass
        #self.undoStack.push(pairedFunctionCommand(function = self._leastCostAutofit,inverseFunction=self._dropRows,description='least cost autofit'))

    
   
    def _leastCostAutofit(self):
      #  print('_sequencialScoreAutofit',self.run)
        if self.run is not None:
           r = {'pks':self.runQuery('select pk from hsrr.least_cost_autofit(%(run)s)', {'run': self.run()})}
           self.select()
           return r


    def sectionLabels(self,rows):
        col = self.fieldIndex('sec')
        return [self.index(r,col).data() for r in rows]



    def sectionLabel(self,index):
        col = self.fieldIndex('sec')
        return self.index(index.row(),col).data()
    
    
    
    #list of turples [(start,end)] for rows
    def runChainages(self,rows):
        sCol = self.fieldIndex('ch')
        eCol = self.fieldIndex('e_ch')
        return [(self.index(row,sCol).data(),self.index(row,eCol).data()) for row in rows]



#run query and get result of 1st line
    def singleLineQuery(self, query,args):
        c = self.con()
        if c is not None:
            cur = c.cursor()
            cur.execute(query,args)
            return cur.fetchone()



    def selectOnLayers(self,rows):        
        self._networkModel.selectSectionsOnlayer(self.sectionLabels(rows))
        self._readingsModel.selectOnLayer(self.runChainages(rows))
        layer_functions.zoomToFeatures(self._networkModel.selectedFeatures()+self._readingsModel.selectedFeatures())
            
    
    
    