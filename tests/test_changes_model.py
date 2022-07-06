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



def testSetData(m):
    i = m.index(0,m.fieldIndex('sec'))
    m.setData(i,'4720A62/190')



if __name__ =='__console__':
    db = get_db.getDb()
    m = createChangesModel()
   # print(testInsertDummy(m))
    m.setRun('A1 SB RE')
    #no readings in this run
    testSetData(m)
 #   testSequencialAutofit(m)

