# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 11:42:07 2022

@author: Drew.Bennett
"""

import psycopg2

from PyQt5.QtWidgets import QUndoCommand

from hsrr_processor.models import commands


def dbToCon(db):
    return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password()) 




class dropRunsCommand(QUndoCommand):
    
    def __init__(self,runs,routeModel,readingsModel,runInfoModel,parent=None,description='drop runs'):
        super().__init__(description,parent)
        
        routesCommand = commands.dropRunsCommand(model=routeModel,runs=runs,parent=self)
        readingsCommand = commands.dropRunsCommand(model=readingsModel,runs=runs,parent=self)
        runInfoCommand = commands.dropRunsCommand(model=runInfoModel,runs=runs,parent=self)
    
        #chaining commands together by setting parent.

        
        

            
            