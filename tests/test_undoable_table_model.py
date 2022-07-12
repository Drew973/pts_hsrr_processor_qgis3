
from hsrr_processor.models.undoable_table_model.undoable_table_model import undoableTableModel
from PyQt5.QtSql import QSqlTableModel

from hsrr_processor.tests import get_db


db = get_db.getDb()
m = undoableTableModel(db)
m.setTable('hsrr.routes')
m.setEditStrategy(QSqlTableModel.OnFieldChange)
m.select()



def testDropRows(m):
    c = m.rowCount()
    print(c)
    m.dropRows([0,1])
    m.select()
    assert m.rowCount() == c-2 or m.rowCount()==0

    m.undo()
    m.select()
    assert m.rowCount() == c

    m.redo()
    m.select()
    #assert m.rowCount() == c-2



testDropRows(m)



