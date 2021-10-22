from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QUndoCommand,QTableView,QUndoStack
import psycopg2



'''
command to update QSqlTableModel.
uses primary key(s) to find index and calls QSqlTableModel.setData()
'''
class updateCommand(QUndoCommand):

    def __init__(self,index,value,description='update',parent=None):
        super().__init__(description,parent)
        self.model = index.model()
        self.column = index.column()
        #self.pk = index.model().indexToPk(index)
        self.oldValue = index.data()
        self.newValue = value
        self.primaryVals = index.model().primaryValues(index.row())#values of primary key


    def redo(self):
        index = self.index()
        self.model.setDataCommandLess(index,self.newValue)
        self.primaryVals = index.model().primaryValues(index.row())#might change primary values


    def undo(self):
        index = self.index()
        self.model.setDataCommandLess(index,self.oldValue)
        self.primaryVals = index.model().primaryValues(index.row())#might change primary values


#gets model index from self.primaryVals
    def index(self):
        for i in range(self.model.rowCount()):
            if self.model.primaryValues(i)==self.primaryVals:
                return self.model.index(i,self.column)








'''
command to insert data into model.

'''
class insertCommand(QUndoCommand):

    def __init__(self,model,data, description='insert'):
        super().__init__(description)
        self.model = model
        self.data = data


    def redo(self):
        with self.model.con() as con:
            self.pks = insert(con.cursor(cursor_factory=psycopg2.extras.DictCursor),self.model.tableName(),self.data,self.model.primaryKeyNames())
            print('redo:',self.pks)


    def undo(self):
        with self.model.con() as con:
            delete(con.cursor(cursor_factory=psycopg2.extras.DictCursor),self.model.tableName(),self.pks)


'''
#use dictcursor to get data suitable to use with insert
pks: list like of dict like. deletes where key=value and key2=value2...
'''
def delete(cur,table,pks,returning=''):
    if returning:
        if isinstance(returning,list):
            returning ='returning '+','.join(returning)
        else:
            returning = 'returning ' + returning
        
   # '(a=b and c=d) or ()'...
    condition= ' or '.join([rowCondition(pk) for pk in pks])
        
    q = 'delete from {table} where {condition} {returning}'
    q = q.format(table=table,condition=condition,returning=returning)
    cur.execute(q)
    return cur.fetchall()


def rowCondition(pk):
    return '('+' and '.join([str(k)+'='+str(pk[k]) for k in pk])+')'


'''
data:list like of dict like [{}]
need same keys for every row

returning: list like of columns to return
returns cur.fetchall()
should probaly look into sql injection...
'''

def insert(cur,table,data,returning=''):
    
    if returning:
        returning ='returning '+','.join(returning)
    
    columns = list(data[0].keys())
        
    a = ','.join(['%('+col+')s' for col in columns ])   # eg  %(run)s,%(sec)s
    vals = ','.join([cur.mogrify("("+a+")",row).decode() for row in data])
           
    q = "insert into {table} ({columns}) VALUES {vals} {returning};"
    q = q.format(table=table,columns=','.join(columns),vals=vals,returning=returning)
    cur.execute(q)
    return cur.fetchall()
    
    

class undoableTableModel(QSqlTableModel):
    
    def __init__(self,parent,db,undoStack):
        super().__init__(parent,db)
        self.undoStack = undoStack
        self.pkCols = ['pk']


    def con(self):
        db = self.database()
        return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())


#calls QSqlTableModel.setData()
    def setDataCommandLess(self, index, value, role=Qt.EditRole):
        super().setData(index, value,role)



    def runUndoCommand(self,command):
        if self.undoStack is None:
            command.redo()
        else:
            self.undoStack.push(command)
            
    
    #parent is parent for QUndoCommand to push
    def setData(self, index, value, role=Qt.EditRole,parent=None,description='set data'):
        if role == Qt.EditRole:
            current = self.data(index,role)
            if current!=value:
                self.runUndoCommand(updateCommand(index,value,description=description,parent=parent))
            return True
        
        return QSqlTableModel.setData(self, index, value, role)
    
    
    #returns 1st row where primaryValues == values
    def findPrimaryValues(self,values):
         for i in range(self.rowCount()):
            if self.primaryValues(i) == values:
                return i
         
  #inserts list of dict like.
   # [{}]
   # returns primary keys.
    def insert(self,data):
        self.runUndoCommand(insertCommand(self,data))
        self.select()
    
     #def insert(self,data)
     
     #def delete(self,pks)
 
    def primaryKeyNames(self):
        return [self.primaryKey().fieldName(i) for i in range(self.primaryKey().count())]
 
    
if __name__=='__console__' or __name__=='__main__':
    data = [{'run':'SEW NB CL1','sec':'D','ch':-110},{'run':'SEW NB CL1','sec':'D','ch':-10}]
    
    from PyQt5.QtSql import QSqlDatabase
    QSqlDatabase.removeDatabase('site cat test')
    db = QSqlDatabase('QPSQL')
    db.close()
    db.setHostName('localhost')
    db.setDatabaseName('test')
    db.setUserName('postgres')
    print(db.open())

    v = QTableView()
    
    u = QUndoStack()
    m = undoableTableModel(parent=v,db=db,undoStack=u)
    m.setTable('hsrr.section_changes')
    m.setEditStrategy(QSqlTableModel.OnFieldChange) 
    m.setSort(m.fieldIndex('sec'),Qt.AscendingOrder)
    m.select()
    
    v.setModel(m)
    
    v.show()