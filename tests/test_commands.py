import os
import sys

pluginFolder = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\hsrrprocessor'
sys.path.append(pluginFolder)

#import unittest
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtWidgets import QUndoStack


#from context import runInfoModel,commands
from hsrrprocessor import commands
from models import runInfoModel,changesModel
#works in qgis python console.


import logging

logging.basicConfig(filename=r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\hsrrprocessor\tests\test.log',
                    level=logging.DEBUG,filemode='w')


def getDb():
    QSqlDatabase.removeDatabase('test')
    db = QSqlDatabase.addDatabase('QPSQL','test')
    db.close()
    db.setHostName('localhost')
    db.setDatabaseName('test')
    db.setUserName('postgres')
    print('db opened:',db.open())
    return db


#tests upload command and reverse with fresh data .readings should be empty after this.
def testUpload():
    db = getDb()
    u = QUndoStack()
    runModel = runInfoModel.runInfoModel(db=db,undoStack=u)
    runModel.dropRuns(['SEW NB CL1'])
    uris = [r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\hsrrprocessor\tests\example_data\SEW NB CL1.xls']
    c = commands.uploadRunsCommand(runInfoModel=runModel,uris=uris)
    c.redo()
    c.undo()


def testDrop():
    db = getDb()
    u = QUndoStack()
    runModel = runInfoModel.runInfoModel(db=db,undoStack=u)
    cm = changesModel.changesModel(db=db,undoStack=u)
    runs = ['SEW NB CL1']
    c = commands.dropRunsCommand(runInfoModel=runModel,runs=runs,sectionChangesModel=cm)
    c.redo()
    c.undo()


if __name__ == '__main__' or __name__ =='__console__':
    testUpload()
    testDrop()
