# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 14:09:03 2022

@author: Drew.Bennett

undo commands used by models.
makes sense to define here as shared between different models.
may need to chain these together eg to drop run.


"""


from PyQt5.QtWidgets import QUndoCommand

import logging
logger = logging.getLogger(__name__)
from hsrr_processor.models import table



class addRunCommand(QUndoCommand):
    
    def __init__(self,model,fileName,parent=None,description = 'upload run'):
        super().__init__(description,parent)
        self.model = model
        self.fileName = fileName
        
        
        
    def redo(self):
        self.run = self.model._addRun(self.fileName)
       


    def undo(self):
        self.model._dropRun(self.run)




'''
command to drop runs.
used by runInfoModel,readingsModel,routes_model.
model needs _dropRuns(runs) method that returns data to be used by _insert(data) method
'''


class dropRunsCommand(QUndoCommand):
    
    def __init__(self,model,runs,parent=None,description='drop runs'):
        super().__init__(description,parent)
        self.model = model
        self.runs = runs



    def redo(self):
        logger.debug('dropRuns.redo(),runs:%s',self.runs)
    
        if hasattr(self.model,'run'): #model has run() method
            self.run = self.model.run()    
            
        self.data = self.model._dropRuns(self.runs)
        
    
    
    def undo(self):
        logger.debug('dropRuns.undo() data:%s',self.data)
        self.model._insert(self.data)

        if hasattr(self.model,'setRun'): #model has setRun method
            self.model.setRun(self.run)
        



class addRunsCommand(QUndoCommand):
    
    def __init__(self,model,data,parent=None,description = 'upload run'):
        super().__init__(description,parent)
        self.model = model
        self.data = data
        
    def redo(self):
        self.result = self.model._addRuns(self.data)
        #generate_run_name is stable postgres function. will give same result here.

    def undo(self):
        self.model._drop(self.result)




class uploadRunsCommand(QUndoCommand):
    
    def __init__(self,files,readingsModel,runInfoModel,parent=None,description='upload runs'):
        super().__init__(description,parent)
        self.files = files
        self.readingsModel = readingsModel
        self.runInfoModel = runInfoModel
        

    def redo(self):
        self.result = self.runInfoModel._addRuns(self.files)#table(run,file)
        self.readingsModel._addRuns(self.result)


    def undo(self):
        self.readingsModel._dropRuns(self.result)
        self.runInfoModel._dropRuns(self.result)#need to do last because foreign key



class combinedDropRunsCommand(QUndoCommand):
    
    def __init__(self,runs,routeModel,readingsModel,runInfoModel,parent=None,description='drop runs'):
        super().__init__(description,parent)
        

        t = table.table(columns=['run'],data=[(r,) for r in runs])   #tuple('abc') = ('a', 'b', 'c')
        
        routesCommand = dropRunsCommand(model=routeModel,runs=runs,parent=self)
        readingsCommand = dropRunsCommand(model=readingsModel,runs=runs,parent=self)
        runInfoCommand = dropRunsCommand(model=runInfoModel,runs=t,parent=self)#need do this last because foreign key.




        


