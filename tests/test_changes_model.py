from hsrr_processor.models import changesModel 
from hsrr_processor.tests import get_db



def createChangesModel(db=get_db.getDb()):
    m = changesModel.changesModel(db)
    return m
    
    

def testInsertDummy(model):
    c = model.rowCount()
    print(c)
    model.insertRow(start_run_ch=0)
    assert model.rowCount()==c+1
    
    model.undo()
    assert model.rowCount()==c

    model.redo()
    assert model.rowCount() == c+1
    


def testSequencialAutofit(model):
    print(model._sequencialScoreAutofit())



def testSetData(m):
    
    ch = 10
    i = m.index(0,m.fieldIndex('start_run_ch'))
    origonal = i.data()
    
    m.setData(i,ch)
    assert i.data()==ch

    m.undo()
    assert i.data()==origonal
    
    m.redo()
    assert i.data()==ch

def testDropRuns(m):
    m.dropRuns(['M621 EB LE'])
    m.undo()


if __name__ =='__console__':
    db = get_db.getDb()
    m = createChangesModel()
    m.setRun('M621 EB LE')

    print(testInsertDummy(m))
    #no readings in this run
    testSetData(m)
 #   testSequencialAutofit(m)
    #testDropRuns(m)
