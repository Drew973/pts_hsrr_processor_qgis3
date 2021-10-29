import os


from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt
import psycopg2

from . import undoableTableModel
import logging

logger = logging.getLogger(__name__)




class runInfoModel(undoableTableModel.undoableTableModel):
    
    def __init__(self,db,undoStack,parent=None):
        super().__init__(parent=parent,db=db,undoStack=undoStack,autoIncrementingColumns=['geom'])
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
        logger.info('dropRuns(%s)'%(str(runs)))
        with self.con() as con:
            cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute('delete from hsrr.run_info where run = any(%(runs)s) returning run,file',{'runs':runs})
            res = [dict(r) for r in cur.fetchall()]
            
        self.select()
        return res


    #add row to run_info table from fileName. Returns run (primary key,generated from hsrr.generate_run_name function)
    def addRun(self,fileName):
        logger.info('addRun(%s)'%(str(fileName)))
        with self.con() as con:
            cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
         #   cur.execute('insert into hsrr.run_info(run,file) values (hsrr.generate_run_name(%(prefered)s),%(uri)s) returning run',
          #              {'prefered':os.path.splitext(os.path.basename(fileName))[0],'uri':fileName})
          
            cur.execute('select hsrr.add_to_run_info(%(fileName)s,%(prefered)s)',
                        {'fileName':fileName,'prefered':os.path.splitext(os.path.basename(fileName))[0]})
            run = cur.fetchone()[0]
        self.select()
        return run
    
    
    