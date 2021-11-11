import os
from PyQt5.QtWidgets import QUndoStack




import hsrr_processor.commands as commands
from hsrr_processor.models import runInfoModel,changesModel

from hsrr_processor.tests import runTests


'''
tests for:
    upload run
    drop run
    
    pass if no errors raised.
    
    if command works then everything called by it works.
'''




import unittest


class test_runInfo(unittest.TestCase):
    
    def setUp(self):
        db = runTests.getDb()
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










