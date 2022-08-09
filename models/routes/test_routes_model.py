
from hsrr_processor.tests import get_db
from hsrr_processor import init_logging
from hsrr_processor.models.routes.main_routes_model import mainRoutesModel



def testInit():
    db = get_db.getDb()

    m = mainRoutesModel(db)
   # m.setDatabase(db)
    return m
    
    
def test_insert(m):
    c = m.rowCount()
    data = {'columns':['run'],'data':[[m.run()]]}
    pks = m._insert(data)
    assert(m.rowCount() == c+1)
    print(pks)
    data = m._drop(pks)
    print(data)
    
   
def testDropRuns(model):
    run = 'M621 EB CL2'
    model.setRun(run)
    c = model.rowCount()
    model.dropRuns([run])
    assert model.rowCount()==0#should have no rows
    model.undo()
    assert model.rowCount()==c#should have origonal rowCount
    
    
    
m = testInit()
testDropRuns(m)
