# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 13:19:09 2022

@author: Drew.Bennett
"""


from PyQt5.QtWidgets import QUndoCommand,QUndoStack


class insertCommand(QUndoCommand):
    
    
    def __init__(self,model,data,description='',parent=None):
        super().__init__(description,parent)
        self.model = model
        self.data = data

        
        
    def redo(self):
        self.pks = self.model._insert(self.data)
        
        

    def undo(self):
        self.model._drop(self.pks)
        
        
        
class dropCommand(QUndoCommand):
    
    
    def __init__(self,model,pks,description='',parent=None):
        super().__init__(description,parent)
        self.model = model
        self.pks = pks

        
        
    def redo(self):
        self.data = self.model._drop(self.pks)        

        

    def undo(self):
        self.model._insert(self.data)        
        
        
        

    
    
class updateCommand(QUndoCommand):
    
    def __init__(self,model,pk,col,value,description='',parent=None):
        super().__init__(description,parent)
        self.model = model
        self.pk = pk
        self.col = col
        self.value = value
    
        
        
    def redo(self):
        self.oldValue = self.model._update(self.pk,self.col,self.value)
        


    def undo(self):
        self.model._update(self.pk,self.col,self.oldValue)

        


'''
abstract class. 
model with undoable create,read,update,delete capabilities.
pushes insert,update,drop commands to QUndoStack

needs some kind of primary Key.



subclasses will need _insert(data) method that returns primary key(s) of new data
subclasses will need _drop(pks) method that returns deleted data
_update(pk,value) that returns old value(s)



'''
from abc import ABC
from PyQt5.QtCore import QObject






class undoableCrudModel(QObject):
        
    
    def __init__(self):
        self.setUndoStack(QUndoStack())
    
  
    
    def update(self,pk,col,value,description=''):
        self.undoStack().push(updateCommand(model=self,col=col,pk=pk,value=value,description=description))

    
    
    def insert(self,data,description=''):
        self.undoStack().push(insertCommand(model=self,data=data,description=description))
    
    
    
    def drop(self,pks,description=''):
        self.undoStack().push(dropCommand(model=self,pks=pks,description=description))

    
    
    def setUndoStack(self,undoStack):
        self._undoStack = undoStack



    def undoStack(self):
        return self._undoStack
        
        
    def undo(self):
        self.undoStack().undo()
        

    def redo(self):
        self.undoStack().redo()        