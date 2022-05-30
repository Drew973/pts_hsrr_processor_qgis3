from hsrr_processor.models import changesModel 
from hsrr_processor.tests import get_db


def createChangesModel(db=get_db.getDb()):
    m = changesModel.changesModel(db)
    return m


def testInsertDummy(model):
    data ={'sec':'D',
                 'xsp':None,
                 'ch':0,
                 'note':'insert test',
                 'startSecCh':0,
                 'endSecCh':0}
    
    model.insertRow(**data)
    model.undo()
    model.redo()


def testSequencialAutofit(model):
    print(model._sequencialScoreAutofit())


if __name__ =='__console__':
    db = get_db.getDb()
    m = createChangesModel()
    print(testInsertDummy(m))
    m.setRun('M62 NB CL1 J22-J23')
    testSequencialAutofit(m)

