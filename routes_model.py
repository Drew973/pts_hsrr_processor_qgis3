from qgis.PyQt.QtSql import QSqlTableModel,QSqlQuery#,QSqlQueryModel
from qgis.PyQt.QtCore import Qt
#from . better_table_model import  



import psycopg2


def dbToCon(db):
    return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())



class routesModel(QSqlTableModel):

    
#db=qsqldatabase
    def __init__(self,db):
        super(routesModel, self).__init__(db=db)

        self.setTable('hsrr.section_changes') 
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.setSort(self.fieldIndex("s_ch"),Qt.AscendingOrder)#sort by s
        self.select()
        self.hiddenColIndexes=[self.fieldIndex(col) for col in ['run','pk','pt','geom']]


    def setRun(self,run):
        self.setFilter("run='%s'"%(run))
        print(self.filter())
        self.select()


    def dropRows(self,indexes):
        for r in sorted([i.row() for i in indexes],reverse=True):
            self.removeRows(r,1)
        self.select()
        
        
    def setXSPs(self,run,xsp):
        q = QSqlQuery('update section_changes set xsp=:xsp where run=:run', db=self.database() )
        q.bindValue(":xsp", "xsp")
        q.bindValue(":run", "run");
        q.exec()
        
      
        
    def addRow(self,run,sec,rev,xsp,ch):
        d={'run':run,'sec':sec,'rev':rev,'xsp':xsp,'ch':ch}      
       # q = 'insert into hsrr.section_changes(run,sec,reversed,xsp,chgeom) values (%(run)s,%(sec)s,%(rev)s,%(xsp)s,%(ch)s)'
        q = 'insert into hsrr.section_changes(run,sec,reversed,xsp,ch,geom) values (%(run)s,%(sec)s,%(rev)s,%(xsp)s,%(ch)s,hsrr.run_ch_to_pt(%(run)s,%(ch)s))'
       
        with dbToCon(self.database()) as con:
            con.cursor().execute(q,d)
            
        self.select()
        
        
        
    def addRow2(self,run,sec,rev,xsp,ch):
        d={'run':run,'sec':sec,'rev':rev,'xsp':xsp,'ch':ch}      
        print(d)
        
        q=QSqlQuery(db=self.database())
              
        q.bindValue(":run", run);
        q.bindValue(":sec", sec)
        q.bindValue(":rev", rev)
        q.bindValue(":xsp", xsp)
        q.bindValue(":ch", ch)
            
        prep = q.prepare('insert into hsrr.section_changes(run,sec,reversed,xsp,ch) values (:run,:sec,:rev,:xsp,:ch)')
         
        if not prep:
            print('prepare failed')
            return
    
        r = q.exec()  
        if not r:
            print('last query:'+q.lastQuery())
            print(q.lastError().databaseText())
       
        q.finish()
        self.select()