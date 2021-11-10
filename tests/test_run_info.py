import os
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtWidgets import QUndoStack




#from context import runInfoModel,commands
import hsrr_processor.commands as commands
from hsrr_processor.models import runInfoModel,changesModel
#works in qgis python console.



def getDb():
    QSqlDatabase.removeDatabase('test')
    db = QSqlDatabase.addDatabase('QPSQL','test')
    db.close()
    db.setHostName('localhost')
    db.setDatabaseName('test')
    db.setUserName('postgres')
    assert db.open(),'could not open database'
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



import unittest


class test_runInfo(unittest.TestCase):
    
    def setUp(self):
        db = getDb()
        u = QUndoStack()
        self.model = runInfoModel.runInfoModel(db=db,undoStack=u)
        self.cm = changesModel.changesModel(db=db,undoStack=u)



    def tearDown(self):
        self.model = None
        self.cm = None
        
    def test_uploadCommand(self):
        uri = os.path.join(os.path.dirname(__file__),'example_data','SEW NB CL1.xls')
        c = commands.uploadRunsCommand(runInfoModel=self.model, uris=[uri])
        c.redo()
        c.undo()


    def test_dropCommand(self):
        runs = ['SEW NB CL1']
        c = commands.dropRunsCommand(runInfoModel=self.model,runs=runs,sectionChangesModel=self.cm)
        c.redo()
        c.undo()










