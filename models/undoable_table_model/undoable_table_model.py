# -*- coding: utf-8 -*-
"""


all hsrr processor models using postgres and submit on Field change
not particularly big tables. performance probably not critical

setData easy.


"""
from PyQt5.QtSql import QSqlTableModel

import logging

logger = logging.getLogger(__name__)

from hsrr_processor.models.routes.undoable_crud_model import undoableCrudModel
from PyQt5.QtCore import Qt



class undoableTableModel(QSqlTableModel,undoableCrudModel):
    
    def __init__(self,db,parent=None):
        logger.debug('__init__()')
        QSqlTableModel.__init__(self,parent,db)
        undoableCrudModel.__init__(self)
        self.useSetDataCommand = False
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.select()    
    
    
    
    #select() calls setData(). Don't want commands for that.
    def select(self):
        self.useSetDataCommand = False
        r = super().select()
        self.useSetDataCommand = True
        return r
        
    
    
    def setData(self, index, value, role=Qt.EditRole):
        logger.debug('setData')
        
        if role==Qt.EditRole and self.useSetDataCommand:
            self.update(pk=self.pk(index.row()),col=self.columnName(index.column()),value=value,description='set data')
            return True
        else:
            return super().setData(index, value, role)    
    
    
    
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
        
        
        
    def dropRows(self,rows):
        pks = [[self.pk(r)] for r in rows]
        self.drop({'columns':['pk'],'data':pks},description='drop rows')



    def pk(self,row):
        return self.primaryValues(row)
    
    
    #col:int ->str
    def columnName(self,col):
        return self.record().fieldName(col)
    
    
    
    #find row index from pk
    def findRow(self,pk):
        for i in range(self.rowCount()):
            if self.pk(i)==pk:
                return i
        return -1        
    