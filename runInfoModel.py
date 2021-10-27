import os


from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt
import psycopg2

from . import undoableTableModel
import logging

logger = logging.getLogger(__name__)




class runInfoModel(undoableTableModel.undoableTableModel):
    
    def __init__(self,parent,db,undoStack):
        super().__init__(parent=parent,db=db,undoStack=undoStack)
        self.setTable('hsrr.run_info')
        self.setSort(self.fieldIndex("run"),Qt.AscendingOrder)
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.select()

        
    def secChangesCount(self,run):
        with self.con() as con:
            cur = con.cursor()
            cur.execute('select count(pk) from section_changes where run = %(run)s',{'run':run})
            return cur.fetchone()[0]
        
        
    def dropRuns(self,runs):
        with self.con() as con:
            cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute('delete from hsrr.run_info where run = any(%(runs)s) returning run,file',{'runs':runs})
            res = [dict(r) for r in cur.fetchall()]
            
        self.select()
        return res


    #add row to run_info table from fileName. Returns run (primary key,generated from hsrr.generate_run_name function)
    def addRun(self,fileName):
        logger.info('addRun()',fileName)
        with self.con() as con:
            cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute('insert into hsrr.run_info(run,file) values (hsrr.generate_run_name(%(prefered)s),%(uri)s returning run)',
                        {'prefered':os.path.splitext(os.path.basename(fileName))[0],'uri':fileName})
            run = cur.fetchone()[0]
        self.select()
        return run