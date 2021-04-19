from qgis.PyQt.QtSql import QSqlTableModel#,QSqlQueryModel
from qgis.PyQt.QtCore import Qt


class betterTableModel(QSqlTableModel):

    def __init__(self,db):
        super(betterTableModel, self).__init__(db=db)
        self.colorFunction=None
        self.colsEditable=None #dict of column index and bool


    def setTable(self,table):
        QSqlTableModel.setTable(self,table)
        self.colsEditable={col:True for col in range(0,self.columnCount())}#dict of column index:editable 


 #index=qmodelindex 
    #called by model to refresh tableviews etc
    def data(self, index, role):
        if role == Qt.BackgroundRole:
            if self.colorFunction:
                if self.colorFunction(index):
                    return self.color_function(index)
                
        return QSqlTableModel.data(self, index, role);


#sets function to determine colour of cell given index. Function should return QBrush,False or None.    
    def setColorFunction(self,function):
        self.color_function=function


#set editibility of column index col to bool Editable.
    def setColEditable(self,col,editable):
        self.colsEditable[col]=editable


#set all editiaility of all columns to editable
    def setEditable(self,editable):
        for k in self.colsEditable:
            self.colsEditable[k]=editable


     #flags determine if item editable      
    def flags(self,index):
        if self.colsEditable[index.column()]:
            return QSqlTableModel.flags(self,index)
        else:
            #Qt.ItemIsEnabled,Qt.ItemIsEditable,Qt.ItemIsSelectable
            return QSqlTableModel.flags(self,index)^Qt.ItemIsEditable #^=xor
                   

