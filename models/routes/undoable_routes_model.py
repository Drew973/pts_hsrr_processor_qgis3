# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 12:59:33 2022

@author: Drew.Bennett

QSqlQueryModel subclass. Has undoable updating,inserting and deleting

model responsible for editing route data.

QSqlTable better? doesn;t rearrange rows when data changed.
view doesn't lose selection when data changed

"""

import psycopg2
from PyQt5.QtSql import QSqlTableModel

import logging
logger = logging.getLogger(__name__)

from hsrr_processor.models.routes.undoable_crud_model import undoableCrudModel,updateCommand
from hsrr_processor.models import commands


import psycopg2.extras#not always imported with import psycopyg2. version dependent.


from PyQt5.QtCore import Qt


from PyQt5.QtWidgets import QUndoCommand



'''
    command to autofit run.
    method is method of model to call.
    calls method(run)
    and model.drop() with result of this
'''

class autofitCommand(QUndoCommand):
    
    def __init__(self,model,method,run,parent=None,description='autofit'):
        super().__init__(description,parent)
        self.model = model
        self.run = run
        self.method = method


    def redo(self):
        logger.debug('autofitCommand.redo() method:%s,run:%s',self.method,self.run)
        self.pks = self.method(self.run)
    
    
    def undo(self):
        logger.debug('autofitCommand.drop() pks:%s',self.pks)
        self.model._drop(self.pks)



#doing all updates in 1 query would be more efficient. but performance seems fine as is.
class setXspCommand(QUndoCommand):
    
    def __init__(self,model,xsp,description='set XSP',parent=None):
        super().__init__(description,parent)

        for i in range(0,model.rowCount()):
            c = updateCommand(model,model.pk(i),'xsp',xsp,parent=self)
    
  


class undoableRoutesModel(QSqlTableModel,undoableCrudModel):
    
    
    def __init__(self,db,parent=None):
        logger.debug('__init__()')
        print(parent,db)
        QSqlTableModel.__init__(self,parent,db)
       # super(QSqlTableModel,self).__init__(parent,db)
        undoableCrudModel.__init__(self)
        self.useSetDataCommand = False
        self.setTable('hsrr.routes')
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.setRun('')
        

    
    def setRun(self,run):
        self._run = run
        f = "run = '{run}' order by start_run_ch, NULLIF( sec,'D') NULLS FIRST".format(run=run)#start_run_ch,dummys,other sections
        self.setFilter(f)
        self.select()
    
    
    
    def run(self):
        return self._run
    
    
    
    #data like{'columns':[],'data':[]}
    def _insert(self,data):
        q = 'insert into hsrr.routes({cols}) values {vals} returning pk'.format(cols=','.join(data['columns']),vals='%s')
        
        logger.debug(q)
        
        with self.con() as c:
            if c is not None:
                cur = c.cursor()
                r = psycopg2.extras.execute_values(cur,q,data['data'],fetch=True)
            
        self.select()
        return {'columns':'pk','data':r}
    
    
    
    def addRow(self,startRunCh):
        self.insert({'columns':['run','start_run_ch'],'data':[[self.run(),startRunCh]]})
        
        
    
    def select(self):
        self.useSetDataCommand = False
        r = super().select()
        self.useSetDataCommand = True
        return r
    
    
    def _update(self,pk,col,value):
        logger.debug('update(%s,%s,%s)',pk,col,value)
        row = self.findRow(pk)
        if row ==-1:
            logger.error('pk %s not found',pk)
        else:
            index = self.index(row,self.fieldIndex(col))
            oldVal = index.data()
            super().setData(index,value)
            return oldVal
        
    
    #find row index from pk
    def findRow(self,pk):
        col = self.fieldIndex('pk')
        for i in range(self.rowCount()):
            if self.index(i,col).data()==pk:
                return i
            
        return -1    
    
    
    #setData is called by select().
    #don't want undocommands for this
    
    def setData(self, index, value, role=Qt.EditRole):
        logger.debug('setData')
        
        if role==Qt.EditRole and self.useSetDataCommand:
            self.update(pk=self.pk(index.row()),col=self.columnName(index.column()),value=value,description='set data')
            return True
        else:
            return super().setData(index, value, role)    
    
    
    
    def dropRows(self,rows):
        pks = [[self.pk(r)] for r in rows]
        self.drop({'columns':['pk'],'data':pks},description='drop rows')
        
        
    
    def dropRuns(self,runs):
        self.undoStack().push(commands.dropRunsCommand(model=self,runs=runs))
    
    
    
    def _dropRuns(self,runs):
        q = 'delete from hsrr.routes where run = any(%(runs)s) returning pk,run,start_run_ch,end_run_ch,sec,xsp,start_sec_ch,end_sec_ch,note'
        r = self.runQuery(q,{'runs':runs})
        
      #  if self.run() in runs:
       #     self.setRun('')
    
        return r
    
    
    
    def simpleAutofit(self):
        self.undoStack().push(autofitCommand(model=self,run=self.run(),method=self._simpleAutofit,description = 'simple autofit'))
    
    
    
    def _simpleAutofit(self,run):
        q = 'select pk from hsrr.simple_autofit(%(run)s)'
        r = self.runQuery(q,{'run':run})
        self.select()
        return r
    
    
    
    def leastCostAutofit(self):
        self.undoStack().push(autofitCommand(model=self,run=self.run(),method=self._leastCostAutofit,description = 'least cost autofit'))
    
    
    
    def _leastCostAutofit(self,run):
        q = 'select pk from hsrr.least_cost_autofit(%(run)s)'
        r = self.runQuery(q,{'run':run})
        self.select()
        return r
    
    
    
    #{'columns','data':}
    def _drop(self,pks):
        
        pks = [r[0] for r in pks['data']]
        
        q = 'delete from hsrr.routes where pk = any(%(pks)s) returning pk,run,start_run_ch,end_run_ch,sec,xsp,start_sec_ch,end_sec_ch,note'
        r = self.runQuery(q,{'pks':pks})
         
        self.select()
        return r
    
        
    
    def columnName(self,col):
        return self.query().record().fieldName(col)
    
    
    
    def pk(self,row):
        return self.index(row,self.fieldIndex('pk')).data()
    
    
    
    def setXsp(self,xsp=''):
        self.undoStack().push(setXspCommand(model=self,xsp=xsp))
    
    
    
    def runQuery(self,query,args):
        with self.con() as c:
            if c:
                cur = c.cursor()
                cur.execute(query,args)
                return {'columns':[desc[0] for desc in cur.description],'data':[r for r in cur.fetchall()]}
                
    
    
    #psycopg2 connection. 
    def con(self):
        db = self.database()
        try:
            return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())
        except:
            return None
        
        
        
    def flags(self,index):
        if index.column() != self.fieldIndex('pk'):
            return Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsEnabled
        return Qt.NoItemFlags
        
        
        