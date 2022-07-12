# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 12:59:33 2022

@author: Drew.Bennett

QSqlQueryModel subclass. Has undoable updating,inserting and deleting

model responsible for editing route data.

ui like selecting on layers and converting chainage to coordinates handled by main_routes_model



"""

import psycopg2
from PyQt5.QtSql import QSqlQuery,QSqlQueryModel

import logging
logger = logging.getLogger(__name__)

from hsrr_processor.models.routes.undoable_crud_model import undoableCrudModel
import psycopg2.extras#not always imported with import psycopyg2. version dependent.


from PyQt5.QtCore import Qt



class undoableRoutesModel(QSqlQueryModel,undoableCrudModel):
    
    
    def __init__(self,parent=None):
        logger.debug('__init__()')
        super(QSqlQueryModel,self).__init__()
        super(undoableCrudModel,self).__init__()
        self.setParent(parent)
    
    
    def setDatabase(self,db):
        logger.debug('setDb')
        #self.setQuery('select * from hsrr.routes',db)
        self._db = db
    

    
    def database(self):
        return self._db
    
    
    
    def setRun(self,run):
        self._run = run
        q = QSqlQuery(self.database())
        logger.debug(q)
        #ordered by start_run_ch then sec with 'D' first
        q.prepare("select pk,start_run_ch,end_run_ch,sec,start_sec_ch,end_sec_ch,note from hsrr.routes where run = :run order by start_run_ch, NULLIF( sec,'D') NULLS FIRST")
        q.bindValue(':run',run)
        q.exec()
        logger.debug(q.lastQuery())
        
        logger.debug(q)
        
        self.setQuery(q)
        
    
    
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
    
    
    
    def select(self):
        self.setRun(self.run())
    
    
    
    # pk like {'pk':,'col':,:}
    def _update(self,pk,col,value):
        
        q = 'update hsrr.routes set {col} = {val} where pk = {pk} returning (select {col} from hsrr.routes where pk ={pk})'
    
        q = q.format(col=col,val='%(val)s',pk='%(pk)s')
        
        self.runQuery(q,{'pk':pk,'val':value})
        self.select()
    
    
    
    def setData(self, index, value, role=Qt.EditRole):
        
        if role==Qt.EditRole:
            self.update(pk=self.pk(index.row()),col=self.columnName(index.column()),value=value)
            return True
        else:
            return super().setData(index, value, role)    
    
    
    
    #{'columns','data':}
    def _drop(self,pks):
        
        pks = [r[0] for r in pks['data']]
        
        q = 'delete from hsrr.routes where pk = any(%(pks)s) returning pk,run,start_run_ch,end_run_ch,sec,start_sec_ch,end_sec_ch,note'
        r = self.runQuery(q,{'pks':pks})
        
        self.select()
        return r
    
        
    
    #name : str with column name
    def fieldIndex(self,name):
        return self.query().record().indexOf(name)
    
    
    
    def columnName(self,col):
        return self.query().record().fieldName(col)
    
    
    
    def pk(self,row):
        return self.index(row,self.fieldIndex('pk')).data()
    
    
    
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
        
        
        
        
    #methods for selecting on layers:



        
        
    #methods for chainage widget
        
        
        
        
        
        
        
        
        
        
        