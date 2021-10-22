from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt
import psycopg2
from . import uploadReadings
from PyQt5.QtWidgets import QUndoCommand



def dbToCon(db):
    return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())


'''
    other commands should be added to stack after adding to section_changes...
    unless other user changes it.
    ensure nothing in section_changes before this?
    
'''
class uploadCommand(QUndoCommand):

    def __init__(self,model,readings,description='upload readings',parent=None):
        super().__init__(description,parent)
        self.model = model
        self.readings = readings


    def redo(self):
        self.run = self.model.uploadReadings(self.readings)


    def undo(self):
        if self.model.secChangesCount(self.run)==0:
            self.model.dropRuns([self.run])
        else:
            pass


'''
    data in run_info,readings,section_changes
    delete from run_info cascades
    reupload from file vs store readings?
    file location might change so better to store. memory usage?
    
'''
class dropRunCommand(QUndoCommand):

    def __init__(self,model,run,description='upload readings',parent=None):
        super().__init__(description,parent)
        self.model = model
        self.run = run


    def redo(self):
        self.model.dropRun()


    def undo(self):
        if self.model.secChangesCount(self.run)==0:
            self.model.dropRuns([self.run])
        else:
            pass




class runInfoModel(QSqlTableModel):
    
    def __init__(self,db,parent=None):
        super(runInfoModel,self).__init__(parent=parent,db=db)
        
        self.setTable('hsrr.run_info')
        self.setSort(self.fieldIndex("run"),Qt.AscendingOrder)
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.select()
        
    
    def dropRuns(self,runs):
        print(runs)
        with dbToCon(self.database()) as con:
            con.cursor().execute("delete from hsrr.run_info where run=any(%(runs)s::varchar[])",{'runs':"{"+','.join(runs)+"}"})
        self.select()
        
        
    def secChangesCount(self,run):
        with dbToCon(self.database()) as con:
            cur = con.cursor()
            cur.execute('select count(pk) from section_changes where run = %(run)s',{'run':run})
            return cur.fetchone()[0]
        
    def insert(self,data):
        pass
    
    
    def delete(self,pks):
        #dropRuns
        pass
        
    def uploadReadings(self,uri):
        with dbToCon(self.database()) as con:
             uploadReadings.uploadReadings(uri,con)
        
        self.select()
             
        
    def chainageToPoint(self,chainage):
         pass
     
        
    def pointToChainage(self,chainage):
         pass
        
    #def is_uploaded(self,file):
     #   r=self.sql('select run from hsrr.run_info where file=%(file)s;',{'file':file},ret=True)
      # # print(r)
       # if r:
        #    return True
        #else:
         #   return False        