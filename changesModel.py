#from qgis.PyQt.QtCore import Qt
#from . better_table_model import  

from PyQt5.QtSql import QSqlTableModel#,QSqlRelationalTableModel,QSqlRelation
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QUndoCommand


import psycopg2

from . import undoableTableModel


def dbToCon(db):
    return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())


'''
command to use with method/function and inverse that take single argument and 
return single argument


calls method(args). stores returned value. undo calls inverseMethod() on this
pass method like changesModel.insert
'''

class methodCommand(QUndoCommand):

    def __init__(self,method,arg,inverseMethod,description='',parent=None):
        super().__init__(description,parent)
        self.method = method
        self.arg = arg
        self.inverseMethod = inverseMethod


    def redo(self):
        self.reverseArg = self.method(self.arg)


    def undo(self):
        self.arg = self.inverseMethod(self.reverseArg)
        #update arg to allow for non deterministic eg serial primary key returned after insert command
        


'''
    command to update multiple indexes. uses undoableTableModel.updateCommand s.
    data like [{index:value}]
'''
class multiUpdateCommand(QUndoCommand):

    
    def __init__(self,data,description='multiple update',parent=None):
        super().__init__(description,parent)
        for k in data:
            undoableTableModel.updateCommand(index=k,value=data[k],parent=self)




class changesModel(undoableTableModel.undoableTableModel):
#class changesModel(QSqlRelationalTableModel):

    
#db=qsqldatabase
    def __init__(self,parent,db,undoStack):
        super().__init__(parent=parent,db=db,undoStack=undoStack)

        self.setTable('hsrr.section_changes') 
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.setSort(self.fieldIndex("ch"),Qt.AscendingOrder)#sort by s
        self.select()
        self.hiddenColIndexes=[self.fieldIndex(col) for col in ['run','pk','pt']]
        #self.setRelation(self.fieldIndex('sec'),QSqlRelation('hsrr.network','sec','sec'))
        #self.setJoinMode(QSqlRelationalTableModel.LeftJoin	)
        self.run = None


    def setRun(self,run):
        filt = "run='%s'"%(run)
        self.setFilter(filt)
        self.select()
        self.run = run


    #drop rows with primary keys in pks
    #returns all dropped data.
    def drop(self,pks):        
        with dbToCon(self.database()) as con:
            cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute('delete from hsrr.section_changes where pk =any(%(pks)s) returning *',{'pks':pks})
            res = [r for r in cur.fetchall()]#commits and closes conenction here
        self.select()
        return res
 
    
    
    def pks(self,run):
        with dbToCon(self.database()) as con:
            cur = con.cursor()
            cur.execute('select pk from hsrr.section_changes where run = %(run)s',{'run':run})
        return [r[0] for r in cur.fetchall()]
    
    
    
    #returns QundoCommand to drop primary keys pks
    def dropCommand(self,pks,description=''):
        return methodCommand(self.drop,pks,self.insert,description)
        
    
    #iterable of subscriptible like [{'run':run,'sec':sec...}]. can have extra columns in data.
    #returns primary keys of new rows
    def insert(self,data):
        print(data)
        with dbToCon(self.database()) as con:
            cur = con.cursor()
            
            vals = [cur.mogrify('(%(run)s,%(sec)s,%(reversed)s,%(xsp)s,%(ch)s,%(note)s,%(start_sec_ch)s,%(end_sec_ch)s)',d).decode() for d in data]
            #mogrify returns bytes string with values substrituted.
            q = 'insert into hsrr.section_changes(run,sec,reversed,xsp,ch,note,start_sec_ch,end_sec_ch) values'+','.join(vals)+' returning pk'
            cur.execute(q)
            res = [r[0] for r in cur.fetchall()]#commits and closes conenction here
        self.select()
        return res


    #returns QUndoCommand to insert data.
    #data like [{sec:...}] keys=column names
    def insertCommand(self,data,description=''):
        return methodCommand(self.insert,data,self.drop,description)


    #execute_batch can return results in psycopg2 >=2.8
    #autofit run, returning primary keys of new rows
    def topologyAutofit(self,arg=None):
        if not self.run is None:
            with dbToCon(self.database()) as con:
                cur = con.cursor()
                cur.execute('select hsrr.topology_based_autofit(%(run)s)',{'run':self.run})
                res = [r[0] for r in cur.fetchall()]
            self.select()
            return res


#returns command to set xsp
    def setXspCommand(self,xsp,description='set xsp'):
        col = self.fieldIndex('xsp')
        return multiUpdateCommand(data={self.index(row,col):xsp for row in range(self.rowCount())},description=description)

        
    # data like [{pk:,sec:}...]
    #return origonal values
    #for each dict in data:
        #get origonal values of keys as dict
        #add to results
        