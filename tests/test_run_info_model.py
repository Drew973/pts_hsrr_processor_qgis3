from hsrr_processor.models import run_info_model
from hsrr_processor.tests import get_db
from hsrr_processor import init_logging


def getModel(db = get_db.getDb()):
    return run_info_model.runInfoModel(db=db,parent=None)


#test for _addRuns() and _drop methods
def test_addRuns(m):
    fileNames =['a','b','c']
    c = m.rowCount()
    r = m._addRuns(fileNames)
    print(r)
    assert m.rowCount() == c+3
    
    print(m._drop(r))#fileNames same as run names
    assert m.rowCount() == c


def testAddRuns(m):
    fileNames = ['a','b','c']
    m._dropRuns(fileNames)
    c = m.rowCount()
    m.addRuns(fileNames)
    assert m.rowCount() == c+3
    m.undo()
    assert m.rowCount()==c


m = getModel()
#test_addRuns(m)
testAddRuns(m)
