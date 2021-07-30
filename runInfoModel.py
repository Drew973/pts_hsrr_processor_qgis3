from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt
import psycopg2
from . import uploadReadings




def dbToCon(db):
    return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())




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
        
        
        
        
    def uploadReadings(self,uri):
        with dbToCon(self.database()) as con:
             uploadReadings.uploadReadings(uri,con)
        
        self.select()
             
             
        
    #def is_uploaded(self,file):
     #   r=self.sql('select run from hsrr.run_info where file=%(file)s;',{'file':file},ret=True)
      # # print(r)
       # if r:
        #    return True
        #else:
         #   return False        