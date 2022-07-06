# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 10:12:57 2022

@author: Drew.Bennett
"""


from PyQt5.QtSql import QSqlTableModel
from qgis.PyQt.QtCore import Qt



class coverageModel(QSqlTableModel):
    
    
    def __init__(self,db,parent=None):
        super().__init__(parent=parent,db=db)

        self.setTable('hsrr.requested')
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
    
        self.editableCols = [self.fieldIndex(c) for c in ['note']]
        self.setSort(self.fieldIndex("sec"),Qt.AscendingOrder)
    
    
        
    def sectionLabels(self,rows):
        col = self.fieldIndex('sec')
        return [self.index(r,col).data() for r in rows]
    
    
    
    def flags(self,index):
        if index.column() in self.editableCols:
            return QSqlTableModel.flags(self,index)
     
        else:
          return QSqlTableModel.flags(self,index)^Qt.ItemIsEditable #^=xor
      
        
      
    def showAll(self):
        self.setFilter('')
        self.select()
         
        
         
    def showMissing(self):
        self.setFilter('coverage=0')
        self.select()
      