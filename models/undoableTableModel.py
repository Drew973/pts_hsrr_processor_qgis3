from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QUndoCommand,QTableView,QUndoStack
import psycopg2

from psycopg2 import sql

import logging
logger = logging.getLogger(__name__)


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
class insertDictsCommand(QUndoCommand):

    def __init__(self,model,data, description='insert',parent=None):
        super().__init__(description,parent)
        self.model = model
        self.data = data

    def redo(self):
        self.pks = self.model.insertDicts(self.data)

    def undo(self):
        self.model.deleteDicts(self.data)




'''
command to insert data into model.
'''
class deleteDictsCommand(QUndoCommand):

    def __init__(self,model,pks, description='insert',parent=None):
        super().__init__(description,parent)
        self.model = model
        self.pks = pks

    def redo(self):
        self.data = self.model.deleteDicts(self.pks)
        
    def undo(self):
        self.pks = self.model.insertDicts(self.data)


    

class undoableTableModel(QSqlTableModel):
    
    def __init__(self,parent,db,undoStack,autoIncrementingColumns=[]):
        super().__init__(parent,db)
        self.undoStack = undoStack
        self.autoIncrementingColumns = autoIncrementingColumns


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
         

 
    def primaryKeyNames(self):
        return [self.primaryKey().fieldName(i) for i in range(self.primaryKey().count())]
 
    
 #psycopyg2 sql with schema and tablename
    def tableIdentifier(self):
        a = [sql.Identifier(n) for n in self.tableName().split('.')]
        return sql.SQL('.').join(a)
    
    
     
    '''
    should work with any table.
    insert iterable of subscriptable with key for each non autoincremanting column
    autoincrementing columns and extra keys ignored.
    like [{columnName:value}]
    returns list of psycopg2.extras.DictRow with primary key(s)
    new rows won't necessarily match filter.
    
    con,columnsToInsert,tableName,primaryKeyColumns
    '''
    def insertDicts(self,data):
        logger.info('insertDicts(%s)',str(data))
        
        if len(data)==0:
            #raise ValueError('recieved empty list')
            return []
        
        with self.con() as con:
            cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cols = self.columnsToInsert()
            #vals = ','.join([valString(cur,d,cols) for d in data])
          
            q = sql.SQL("insert into {table} ({fields}) values {values} returning {toReturn}").format(
            fields = sql.SQL(',').join([sql.Identifier(c) for c in cols]),
            table = self.tableIdentifier(),
            values = sql.SQL(',').join([valRow(d,cols) for d in data]),
            toReturn = sql.SQL(',').join([sql.Identifier(c) for c in self.primaryKeyColumns()])
            )

            cur.execute(q)

        res = [dict(r) for r in cur.fetchall()]
      
        self.select()
        return res


   #data like [{columnName:value}]
    #delete from table where key=value, returning all columns.
    
    #con,data,tableIdentifier,columnNames
    def deleteDicts(self,data):
        logger.info('deleteDicts(%s)',str(data))
        
        if data!=[]:
            with self.con() as con:
                cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
                
                q = sql.SQL('delete from {table} where {condition} returning {toReturn}').format(
                table = self.tableIdentifier(),
                condition = sql.SQL(' or ').join([whereCondition(d) for d in data]),
                toReturn = sql.SQL(',').join([sql.Identifier(c) for c in self.columnNames()])
                )
              #  print(cur.mogrify(q))
                cur.execute(q)
                
            self.select()
            return [dict(r) for r in cur.fetchall()]
                #(col_1=val_1 and col_2=val_2) or (col_1=val_3 and col_2=val_4) ...
        else:
            return []



    def primaryKeyColumns(self):
        return [self.primaryKey().fieldName(i) for i in range(self.primaryKey().count())]
 
    
 
    #return empty record to use for inserting etc.
    def newRecord(self):
        r = self.record()
        for c in self.autoIncrementingColumns:
             r.setGenerated(c,False)
        return r
  
    

    def columnNames(self):
        r = self.record()
        return [r.fieldName(i) for i in range(r.count())]



    #list of all non autoincremanting columns
    def columnsToInsert(self):
        r = self.record()
        return [r.fieldName(i) for i in range(r.count()) if not r.fieldName(i) in self.autoIncrementingColumns]


def valRow(data,columns):
    return sql.SQL('(')+sql.SQL(',').join([sql.Literal(data[c]) for c in columns])+sql.SQL(')')




#where condition
#data is dict of column:value
#(col_1=val_1 and col_2=val_2)
#every key needs to be column name
def whereCondition(data):
    if isinstance(data,dict):
        return sql.SQL('(')+sql.SQL(' and ').join( [sql.Identifier(k)+sql.SQL('=')+sql.Literal(data[k]) for k in data])+sql.SQL(')')
    else:
        raise TypeError('whereCondition() requires dictionary but recieved '+str(type(data)))


def test():
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
    m.database()
    v.setModel(m)
    
    v.show()