
from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QUndoCommand,QTableView,QUndoStack
import psycopg2
from psycopg2 import sql


'''
command to insert data into model.
'''
class insertDictsCommand(QUndoCommand):

    def __init__(self,model,data, description='insert'):
        super().__init__(description)
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

    def __init__(self,model,pks, description='insert'):
        super().__init__(description)
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
            
    
    #returns 1st row where primaryValues == values
    def findPrimaryValues(self,values):
         for i in range(self.rowCount()):
            if self.primaryValues(i) == values:
                return i
         
  #inserts list of records.
   # returns primary keys.
    def insertrecords(self,records):
        pks = []
        for r in records:
            self.insertRecord(-1,r)
            #r.keyValues()
            pks.append(self.primaryValues(-1))
        return pks
    
    
     #def delete(self,pk_records)
 
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

    '''
    should work with any table.
    insert iterable of subscriptable with key for each non autoincremanting column
    autoincrementing columns and extra keys ignored.
    like [{columnName:value}]
    returns list of psycopg2.extras.DictRow with primary key(s)
    new rows won't necessarily match filter.
    '''

    def insertDicts(self,data):
        with self.con() as con:
            cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cols = self.columnsToInsert()
            
            vals = ','.join([valString(cur,d,cols) for d in data])
          
            q = sql.SQL("insert into {table} ({fields}) values "+ vals + "returning {toReturn}").format(
            fields = sql.SQL(',').join([sql.Identifier(c) for c in cols]),
            table = sql.Identifier(self.tableName()),
            toReturn = sql.SQL(',').join([sql.Identifier(c) for c in self.primaryKeyColumns()])
            )

            cur.execute(q)
        

        res = [r for r in cur.fetchall()]
      
        self.select()
        return res


    #data like [{columnName:value}]
    #delete from table where key=value, returning all columns.
    def deleteDicts(self,data):
        with self.con() as con:
            cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            q = sql.SQL('delete from {table} where {condition} returning {toReturn}').format(
            table = sql.Identifier(self.tableName()),
            condition = sql.SQL(' or ').join([whereCondition(d) for d in data]),
            toReturn = sql.SQL(',').join([sql.Identifier(c) for c in self.columnNames()])
            )
          #  print(cur.mogrify(q))
            cur.execute(q)
            
        return [r for r in cur.fetchall()]
            #(col_1=val_1 and col_2=val_2) or (col_1=val_3 and col_2=val_4) ...
        

#where condition to find row from primary key
#(col_1=val_1 and col_2=val_2)
#every key needs to be column name
def whereCondition(data):
    return sql.SQL('(')+sql.SQL(' and ').join( [sql.Identifier(k)+sql.SQL('=')+sql.Literal(data[k]) for k in data])+sql.SQL(')')
    
    
def valString(cur,data,columns):
    a = ['%('+c+')s' for c in columns]
    b = '(%s)'%(','.join(a))
    return cur.mogrify(b,dataDict).decode()
        

if __name__=='__console__' or __name__=='__main__':
#    data = [{'run':'SEW NB CL1','sec':'D','ch':-110},{'run':'SEW NB CL1','sec':'D','ch':-10}]
    
    from PyQt5.QtSql import QSqlDatabase
    db = QSqlDatabase('QPSQL')
    db.close()
    db.setHostName('localhost')
    db.setDatabaseName('test')
    db.setUserName('postgres')
    print(db.open())

   # v = QTableView()
    u = QUndoStack()
    m = undoableTableModel(parent=None,db=db,undoStack=u,autoIncrementingColumns=['a'])
    
    m.setTable('insert_test')
    #m.setEditStrategy(QSqlTableModel.OnFieldChange) 
   # m.setSort(m.fieldIndex('a'),Qt.AscendingOrder)
    #m.select()
    
    #r = m.newRecord()
 #   r.setValue('sec', 'B4254/47504963')#works fine with foreign key constraint
  #  res = m.insert([r])
 
    m.select()
   # data = [{'a':1,'sec':'B4254/47504963'},{'a':2,'sec':'A4048/47504973'}]
    print(m.deleteDicts([{'a': 14},{'a':1}]))
    #res = m.insertDicts(data)
    #v.setModel(m)
    #v.show()