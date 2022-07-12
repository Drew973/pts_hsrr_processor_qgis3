# -*- coding: utf-8 -*-
"""
Created on Fri Jul  8 10:12:45 2022

@author: Drew.Bennett


all hsrr processor models using postgres and submit on Field change
not particularly big tables. performance probably not critical

setData easy.



data as dict.? want column names to handle inserting without generated columns.




could do something like 
    delete from table returning all_columns

    not cached...




idealy cached and database independent.

insert with model.insertRecord(record,row)

get row with model.record(row)
drop with model.removeRow(row)



insertRecords(records)
dropRecords(rows)



insertCommand(model,record)


deleting and reinserting. will remove index.
select() will remove indexes.

inserting into specific row and calling select() can change order of records.

model needs _insertRecords(self,records) method.
This needs to return primaryValues of new records.
This can be used to preserve order of records

"""


from PyQt5.QtWidgets import QUndoStack
from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt


import logging
from hsrr_processor.models.undoable_table_model import commands

logger = logging.getLogger(__name__)



def recordToDict(record):
    return {record.fieldName(i):record.value(i) for i in range(record.count())}


class undoableTableModel(QSqlTableModel):
    
    
    def __init__(self,db,parent=None):
        logger.debug('undoableTableModel.__init__')

        super().__init__(parent,db)
        self.setUndoStack(QUndoStack())
        self._useSetDataCommand = True#insertRecord calls setData. ugly workaround to avoid creating update commands through insertRecords.
        
    
    def setUndoStack(self,undoStack):
        self._undoStack = undoStack
        
        
        
    def undoStack(self):
        return self._undoStack
    
    
    
    def undo(self):
        if self.undoStack().canUndo():
            self.undoStack().undo()



    def redo(self):
        if self.undoStack().canRedo():
            self.undoStack().redo()       
        
        
    
    def insertRecords(self,records):
        self.undoStack().push(commands.insertRecordsCommand(self,records))

    
    
    #default implementation. Inserts records at start. subclasses probably want to call select() after this where order matters.
    def _insertRecords(self,records):
        self._useSetDataCommand = False

        logger.debug('undoableTableModel._insertRecords(%s)',records)

        pvs = []
        
        for rec in records:
            
            logger.debug('insertRecords()record:%s',str(recordToDict(rec)))
            if self.insertRecord(0,rec):#calls setData?
                pvs.append(self.primaryValues(0))
        
            else:
                raise ValueError('could not insert record:'+str(recordToDict(rec)))
        
        self._useSetDataCommand = True

        return pvs
    
    
    
    def _setData(self,index,value):
        super().setData(index,value)
        
        
    
    def setData(self, index, value, role=Qt.EditRole):
        logger.debug('undoableTableModel.setData(%s,index,%s)',index,value)
        
    #    return super().setData(index, value, role)##############################to remove

        if role==Qt.EditRole and self._useSetDataCommand:

            self.undoStack().push(commands.setDataCommand(index=index,value=value))
            return True
        else:
            return super().setData(index, value, role)

    
    
    def dropRows(self,rows):
        logger.debug('undoableTableModel.undo()'+str(rows))
        self.undoStack().push(commands.dropRecordsCommand(self,rows))

    
    
    def _removeRecords(self,primaryValues):
        logger.debug('undoableTableModel._removeRecords(%s)',primaryValues)

        records = []
        for r in reversed(range(self.rowCount())):#removing record changes following rows
            if self.primaryValues(r) in primaryValues:
                records.append(self.record(r))
                self.removeRow(r)
       
        return records
    
        
    #row int, 
    #data:keyword arguments like columnName=Value. extras ignored
    def insertRow(self,row=None,**data):
        logger.debug('addRow(%s)',data)
        if row==None:
            row = self.rowCount()
                        
       # self.database().transaction()
        
        rec = self.record()
        
        #remove every field that shouldn't be set by model.
        for i in reversed(range(rec.count())):#count down because removing field will change following indexes.
            fieldName = rec.fieldName(i)
            
            if fieldName in data:
                if data[fieldName] is None:
                    rec.remove(i)
                else:
                    rec.setValue(i,data[fieldName])
            else:
                rec.remove(i)

        self.insertRecords([rec])
        
  