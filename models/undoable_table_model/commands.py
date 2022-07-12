# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 14:09:03 2022
"""


import logging
logger = logging.getLogger(__name__)



from PyQt5.QtWidgets import QUndoCommand



class insertRecordsCommand(QUndoCommand):
    
    def __init__(self,model,records,parent=None,description = 'insert rows'):
        super().__init__(description,parent)
        self.model = model
        self.records = records
        
        
        
    def redo(self):
        logger.debug('insertRecordsCommand.redo()'+str(self.records))
        self.pvs = self.model._insertRecords(self.records)


    def undo(self):
        self.model._removeRecords(self.pvs)





class dropRecordsCommand(QUndoCommand):
    
    def __init__(self,model,rows,parent=None,description = 'drop rows'):
        logger.debug('dropRecordsCommand.__init__()'+str(rows))

        super().__init__(description,parent)
        self.model = model        
        self.pvs = [self.model.primaryValues(row) for row in rows]
        
        
        
    def redo(self):
        logger.debug('dropRecordsCommand.redo()'+str(self.pvs))
        self.records = self.model._removeRecords(self.pvs)



    def undo(self):
        logger.debug('dropRecordsCommand.undo() records=%s',self.records)
        self.pvs = self.model._insertRecords(self.records)




class setDataCommand(QUndoCommand):
    
    def __init__(self,index,value,parent=None,description = 'set data'):
        logger.debug('setDataCommand.__init__()'+str(index))

        super().__init__(description,parent)
        self.model = index.model()
        self.pv =self.model.primaryValues(index.row())
        self.col = index.column()
        self.oldValue = index.data()
        self.newValue = value
        
        
        
    def redo(self):
        logger.debug('setDataCommand.redo()'+str(self.pv))

        row = pvToRow(self.model,self.pv)
        ind = self.model.index(row,self.col)
        
        self.model._setData(ind,self.newValue)
        self.pv = self.model.primaryValues(row)#_setData may have changed these.



    def undo(self):
        logger.debug('setDataCommand.undo().pv:%s,oldValue:%s',self.pv,self.oldValue)
        row = pvToRow(self.model,self.pv)
        ind = self.model.index(row,self.col)
        self.model._setData(ind,self.oldValue)




#gets model index from self.primaryVals
def pvToRow(model,pv):
    for i in range(model.rowCount()):
        if model.primaryValues(i)==pv:
            return i


