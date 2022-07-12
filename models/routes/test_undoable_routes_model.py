
from hsrr_processor.tests import get_db
from hsrr_processor import init_logging
from hsrr_processor.models.routes.undoable_routes_model import undoableRoutesModel



def testInit():
    db = get_db.getDb()

    m = undoableRoutesModel()
    m.setDatabase(db)
    return m
    
    
    
    
def test_insert(m):
    c = m.rowCount()
    data = {'columns':['run'],'data':[[m.run()]]}
    pks = m._insert(data)
    assert(m.rowCount() == c+1)
    print(pks)
    data = m._drop(pks)
    print(data)
    
    
def testInsert(m):
    c = m.rowCount()
    data = {'columns':['run','start_run_ch'],'data':[[m.run(),10]]}
    m.insert(data)
    assert m.rowCount() == c+1
    m.undo()
    assert m.rowCount() == c
    
    
m = testInit()
run = 'M621 EB CL2'
m.setRun(run)

testInsert(m)

#m.addRow(startRunCh=0)

m.update(107,'xsp','test xsp')

v = QTableView()
v.setModel(m)
v.show()

