# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 08:23:14 2022

@author: Drew.Bennett
"""



import psycopg2
from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt

import logging
logger = logging.getLogger(__name__)

from hsrr_processor.models.undoable_table_model import undoable_table_model
import os


from hsrr_processor.models import commands,table
        




class runInfoModel(undoable_table_model.undoableTableModel):
    
    
    def __init__(self,db,parent=None):
        logger.debug('__init__()')
        super().__init__(parent=parent,db=db)
        self.setTable('hsrr.run_info')        
        self.setSort(self.fieldIndex("run"),Qt.AscendingOrder)
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.select()
        
        
        
    #data can be table.
    #or dict like{'columns':[],'data':[]}
    #returns table of pk
    def _insert(self,d):
        logger.debug('insert(%s)',d)

        q = 'insert into hsrr.run_info({cols}) values {vals} returning run'.format(cols=','.join(d['columns']),vals='%s')
        
        logger.debug(q)
        logger.debug('data:%s',d['data'])

        with self.con() as c:
            if c is not None:
                cur = c.cursor()
                runs =  psycopg2.extras.execute_values(cur,q,d['data'],fetch=True)
                logger.debug(runs)
                results = table.table(columns=['run'],data=runs)
            
            
        self.select()
        #return {'columns':['run'],'data':r}
        return results
    
    
    
    #drop where run in table
    def _drop(self,d):
        logger.debug('_drop(%s)',d)

        i = d.fieldIndex('run')
        runs = [r[i] for r in d['data']]

        q = 'delete from hsrr.run_info where run = any(%(runs)s) returning run,file'
        #pks = [r[0] for r in pks['data']]

        logger.debug(q)
        logger.debug('runs:%s',runs)
        #r = self.runQuery(q,{'pks':pks})
        r = self.runQuery(q,{'runs':runs})
         
        self.select()
        return r
    


    #drop list of runs or table of runs.
    def _dropRuns(self,d):
        logger.debug('_dropRuns(%s)',d)

        if not isinstance(d,table.table):
            #d = table.table(columns=['run'],data=[tuple(r) for r in d])
            raise TypeError('_dropRuns requires table')
        
                    
        return self._drop(d)
    
    
    
    def dropRuns(self,runs):
        self.undoStack().push(commands.dropRunsCommand(model=self,runs=runs))
    
    
        
    #psycopg2 connection. 
    def con(self):
        db = self.database()
        try:
            return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())   
        except:
            return None
        
        
        
   # {'columns:[]','data':[]}
    def runQuery(self,query,args):
        with self.con() as c:
            if c:
                cur = c.cursor()
                cur.execute(query,args)
               # return {'columns':[desc[0] for desc in cur.description],'data':[r for r in cur.fetchall()]}
                return table.fromCur(cur)



    def addRuns(self,fileNames):
        self.undoStack().push(commands.addRunsCommand(model=self,data=fileNames))
        
        

    #add list of filenames.
    #returns {'columns':['run','file'],'data':[(run,file)]}
    def _addRuns(self,fileNames):
        
        logger.debug('_addRun(%s)',fileNames)
        q = 'insert into hsrr.run_info(run,file) values %s ON CONFLICT DO NOTHING returning run,file'
        logger.debug(q)
        
        data = [{'short':os.path.splitext(os.path.basename(file))[0],'file':file} for file in fileNames]
        logger.debug(data)
        
        with self.con() as c:
            if c is not None:
                cur = c.cursor()
                result = psycopg2.extras.execute_values(cur,q,data,template='(hsrr.generate_run_name(%(short)s),%(file)s)',fetch=True)

        
        self.select()
        #return {'columns':['run'],'data':result}
        return table.table(columns=['run','file'],data=result)

'''
#runs:list of runs
#returns {'columns':[],'data':[]}
    def _dropRuns(self,runs):
        logger.debug('_dropRun(%s)',runs)
        q = 'delete from hsrr.run_info where run=any(%(runs)s) returning run,file'
        logger.debug(q)
        r = self.runQuery(q,{'runs':runs})
        self.select()
        return r
'''
