#from qgis.PyQt.QtSql import QSqlTableModel,QSqlQuery,QSqlRelation,QRelationalTableModel
#from qgis.PyQt.QtCore import Qt
#from . better_table_model import  

from PyQt5.QtSql import QSqlTableModel,QSqlRelationalTableModel,QSqlRelation
from PyQt5.QtCore import Qt


import psycopg2


def dbToCon(db):
    return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())


class changesModel(QSqlRelationalTableModel):

    
#db=qsqldatabase
    def __init__(self,db):
        super(changesModel, self).__init__(db=db)

        self.setTable('hsrr.section_changes') 
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.setSort(self.fieldIndex("ch"),Qt.AscendingOrder)#sort by s
        self.select()
        self.hiddenColIndexes=[self.fieldIndex(col) for col in ['run','pk','pt']]
        self.setRelation(self.fieldIndex('sec'),QSqlRelation('hsrr.network','sec','sec'))
        self.setJoinMode(QSqlRelationalTableModel.LeftJoin	)


    def setRun(self,run):
        filt = "run='%s'"%(run)
        self.setFilter(filt)
        self.select()


    def dropRows(self,indexes):
        for r in sorted([i.row() for i in indexes],reverse=True):
            self.removeRows(r,1)
        self.select()
        
      
        
    def addRow(self,run,sec='D',rev=None,xsp=None,ch=None):
        d={'run':run,'sec':sec,'rev':rev,'xsp':xsp,'ch':ch}      
       # q = 'insert into hsrr.section_changes(run,sec,reversed,xsp,chgeom) values (%(run)s,%(sec)s,%(rev)s,%(xsp)s,%(ch)s)'
        q = 'insert into hsrr.section_changes(run,sec,reversed,xsp,ch,pt) values (%(run)s,%(sec)s,%(rev)s,%(xsp)s,%(ch)s,hsrr.run_ch_to_pt(%(run)s,%(ch)s))'
       
        with dbToCon(self.database()) as con:
            con.cursor().execute(q,d)
            
        self.select()
        
    
    def autofit(self,run):
        with dbToCon(self.database()) as con:
            con.cursor().execute('select hsrr.autofit(%(run)s)',{'run':run})
        
        self.select()

        
    def setXsp(self,xsp,run):
        with dbToCon(self.database()) as con:
            con.cursor().execute('update hsrr.section_changes set xsp=%(xsp)s where run = %(run)s',{'xsp':xsp,'run':run})
        
        self.select()

        
        
        
       