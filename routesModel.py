#from qgis.PyQt.QtSql import QSqlTableModel,QSqlDatabase#,QSqlQueryModel

from PyQt5.QtSql import QSqlTableModel,QSqlDatabase,QSqlRelationalTableModel,QSqlRelation
from PyQt5.QtCore import Qt


class routesModel(QSqlRelationalTableModel):
    
    
    def __init__(self,parent=None,db = QSqlDatabase()):
        super(routesModel,self).__init__(parent,db)
        self.setTable('hsrr.routes')
        
        self.setRelation(self.fieldIndex('sec'), QSqlRelation("hsrr.network", "sec", "sec"))
        
        
        self.setSort(self.fieldIndex('s_ch'),Qt.AscendingOrder)
        
        
    def setRun(self,run=''):
        
        filt = "run='%s'"%(run)
        print(filt)
        self.setFilter(filt)#documentation wrongly claims setFilter calls select()
        self.select()
        
