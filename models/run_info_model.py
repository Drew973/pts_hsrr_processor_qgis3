import os


from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt
import psycopg2
from PyQt5.QtSql import QSqlQuery

from . import parseReadings
from . import undoableTableModel

from PyQt5.QtWidgets import QUndoStack
import logging

logger = logging.getLogger(__name__)

from hsrr_processor.models import commands




class runInfoModel(undoableTableModel.undoableTableModel):
    
    def __init__(self,db,undoStack = QUndoStack(),parent=None):
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
        self.undoStack.push(commands.dropRunsCommand(model=self,runs=runs))



    def _dropRuns(self,runs):
        with self.con() as con:
            cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute('delete from hsrr.run_info where run = any(%(runs)s) returning run,file',{'runs':runs})
            res = [dict(r) for r in cur.fetchall()]
        self.select()
        return res
    



        
    #data like [(run,file),...]
    #returns pk(run) of new row.
    def _insertRows(self,data):
        logger.debug('_insertRows:'+str(data))
        r = []
        
        if data:
            
                q = 'insert into hsrr.run_info({run,file}) values %s returning run'
        
                with self.con() as con:
                    if con is not None:
                        cur = con.cursor()            
                        r = psycopg2.extras.execute_values(cur,q,data,fetch=True)
                        
                self.select()#select after commiting changes
        return r



        
    def generateRunName(self,fileName):
        prefered = os.path.splitext(os.path.basename(fileName))[0]
        q = QSqlQuery(self.database())
        q.prepare( 'select hsrr.generate_run_name(:prefered)')
        q.bindValue(':prefered',prefered)
        q.exec()
        while q.next():
            return q.value(0)
        


    def addRun(self,fileName):
        run = self.generateRunName(fileName)
        rec = self.record()
        rec.setValue(self.fieldIndex('run'),run)
        rec.setValue(self.fieldIndex('file'),fileName)
        r = self.insertRecord(-1,rec)
        logger.debug('addRun()',fileName,r)
        if r:
            return run
    
    
    
    
    #parse single .xls file and insert into readings table. Need to insert into run_info before calling this.
    #todo:remove readings at 0,0 of espg 4326.
    def uploadSpreadsheet(self,fileName):
        logger.debug('uploadSpreadsheet(%s)'%(fileName))
        run = self.addRun(fileName)

        if run:       
    
            with self.con() as con:
                cur = con.cursor()
                
                q = '''
                insert into hsrr.readings(run,f_line,t,raw_ch,rl,vect,s_ch,e_ch)
                values(
                %(run)s
                ,%(f_line)s
                ,to_timestamp(replace(%(t)s,' ',''),'dd/mm/yyyyHH24:MI:ss')
                ,%(raw_ch)s
                ,%(rl)s
                ,ST_MakeLine(St_Transform(ST_SetSRID(ST_makePoint(%(start_lon)s,%(start_lat)s),4326),27700),St_Transform(ST_SetSRID(ST_makePoint(%(end_lon)s,%(end_lat)s),4326),27700))	
                ,%(line)s * 0.1
                ,%(line)s * 0.1 +0.1
                )
                '''
                psycopg2.extras.execute_batch(cur,q,parseReadings.parseReadings(fileName,run))
    
    
    def uploadSpreadsheets(self,fileNames):
        for f in fileNames:
            self.uploadSpreadsheet(f)