# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 14:09:03 2022

@author: Drew.Bennett

undo commands used by models.
makes sense to define here as shared between different models.
may need to chain these together eg to drop run.


"""


from PyQt5.QtWidgets import QUndoCommand




'''
command to update model.
model needs primaryValues(row) method
_setData(index,value) method
uses primary key(s) to find index and calls QSqlTableModel.setData()
'''
class updateCommand(QUndoCommand):

    def __init__(self,index,value,description='update',parent=None):
        super().__init__(description,parent)        
        self.model = index.model()
        self.column = index.column()
        #self.pk = index.model().indexToPk(index)
        self.oldValue = index.data()
        self.newValue = value
        self.primaryVals = index.model().primaryValues(index.row())#values of primary key


    def redo(self):
        index = self.index()
        self.model._setData(index,self.newValue)
        self.primaryVals = index.model().primaryValues(index.row())#setting data might change primary values


    def undo(self):
        index = self.index()
        self.model._setData(index,self.oldValue)
        self.primaryVals = index.model().primaryValues(index.row())##setting data might change primary values


#gets model index from self.primaryVals
    def index(self):
        for i in range(self.model.rowCount()):
            if self.model.primaryValues(i)==self.primaryVals:
                return self.model.index(i,self.column)







'''
    command to insert data. model needs:
    _insertRows(self,data) method that returns primary keys of new rows.
    _dropRows(self,pks) method that drops rows by primary keys and returns data.
    
'''
class insertCommand(QUndoCommand):

    def __init__(self,model,data,parent=None):
        super().__init__('insert',parent)
        self.model = model
        self.data = data
        
        
    def redo(self):
        self.pks = self.model._insertRows(self.data)


    def undo(self):
        self.data = self.model._dropRows(self.pks)





'''
    command to drop rows model needs:
    _insertRows(self,data) method that returns primary keys of new rows.
    _dropRows(self,pks) method that drops rows by primary keys and returns data.
    
'''
class dropCommand(QUndoCommand):

    def __init__(self,model,pks,parent=None):
        super().__init__('drop',parent)
        self.model = model
        self.pks = pks
        
        
    def redo(self):
        self.data = self.model._dropRows(self.pks)


    def undo(self):        
        self.pks = self.model._insertRows(self.data)
        
        
        

'''
    command to drop runs. model needs:
        
    _dropRuns(self,runs) method that drops runs and returns data.

    _insertRows(self,data) method
    
    will set run through model run() and model.setRun(run) if these methods exist
    
    
'''
class dropRunsCommand(QUndoCommand):

    def __init__(self,model,runs,parent=None):
        super().__init__(parent)
        self.model = model
        self.runs = runs
        self.run = None
        
        
    def redo(self):
        
        if hasattr(self.model,'run'): #model has run() method
            self.run = self.model.run()
            
        self.data = self.model._dropRuns(self.runs)
        

    def undo(self):        
        self.model._insertRows(self.data)
        if hasattr(self.model,'setRun'): #model has setRun method
            self.model.setRun(self.run)
        