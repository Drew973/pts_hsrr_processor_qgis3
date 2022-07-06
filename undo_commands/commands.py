# -*- coding: utf-8 -*-
"""
Created on Tue May 24 12:21:33 2022

@author: Drew.Bennett
"""



from PyQt5.QtWidgets import QUndoCommand

        
        
'''
    QUndoCommand to call function/method with args.
    function needs to return dict of keyword arguments for inverseFunction to use to undo effects of function. 
    treats all arguments as keyword.

'''

class pairedFunctionCommand(QUndoCommand):

    
    #function is any function or method.
    #args: arguments to call it with
    def __init__(self,function,inverseFunction,description='',parent=None,**kwargs):
        super().__init__(description,parent)
        self.function = function
        self.args = kwargs
        self.inverseFunction = inverseFunction



    def redo(self):
        print(self.args)
        self.reverseArgs = self.function(**self.args)



    def undo(self):
       # self.args = self.inverseFunction(self.reverseArgs)
        self.inverseFunction(**self.reverseArgs)
        #update args to allow for non deterministic eg serial primary key returned after insert command
        
        

'''
    command to update multiple indexes. uses undoableTableModel.updateCommand s.
    data like [{index:value}]
'''
class multiUpdateCommand(QUndoCommand):

    
    def __init__(self,data,description='multiple update',parent=None):
        super().__init__(description,parent)
        for k in data:
            updateCommand(index=k,value=data[k],parent=self)




class functionCommand(QUndoCommand):
   
    def __init__(self,function,args,inverseFunction,inverseArgs,description='',parent=None):
        super().__init__(description,parent)
        self.function = function
        self.args = args
        self.inverseFunction=inverseFunction
        self.inverseArgs = inverseArgs

    def redo(self):
        self.result = self.function(**self.args)
        
        
    def undo(self):
        self.inverseResult = self.inverseFunction(**self.inverseArgs)





'''
command to update QSqlTableModel.
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
        self.model.setDataCommandLess(index,self.newValue)
        self.primaryVals = index.model().primaryValues(index.row())#might change primary values


    def undo(self):
        index = self.index()
        self.model.setDataCommandLess(index,self.oldValue)
        self.primaryVals = index.model().primaryValues(index.row())#might change primary values


#gets model index from self.primaryVals
    def index(self):
        for i in range(self.model.rowCount()):
            if self.model.primaryValues(i)==self.primaryVals:
                return self.model.index(i,self.column)

