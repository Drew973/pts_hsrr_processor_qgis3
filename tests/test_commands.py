import sys

if __name__ =='__console__':
    d = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\hsrrprocessor'
    sys.path.insert(0,d)

import unittest


if __name__ =='__console__':
    print('console')
    d = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\hsrrprocessor'
    sys.path.insert(0,d)


from PyQt5.QtSql import QSqlDatabase
import commands
import runInfoModel
from PyQt5.QtWidgets import QUndoStack




def getDb():
    db = QSqlDatabase('QPSQL')
    db.close()
    db.setHostName('localhost')
    db.setDatabaseName('test')
    db.setUserName('postgres')
    print(db.open())
    return db


class TestCommands(unittest.TestCase):
        
    def test_upload(self):
        db = getDb()
        u = QUndoStack()
        runModel = runInfoModel.runInfoModel(db=db,undoStack=u)
        
        uris = [r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\hsrrprocessor\tests\example_data\SEW NB CL1.xls']
        c = commands.uploadRunsCommand(runInfoModel=runModel,uris=uris)
        c.redo()
        
        
if __name__ == '__main__' or __name__ =='__console__':
    #unittest.main()        
    
    print('ok')