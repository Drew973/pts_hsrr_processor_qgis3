# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 10:00:50 2022

@author: Drew.Bennett



simple class to store relational data.
useful for storing query results.


data is list of turples


"""

class table:
    def __init__(self,columns,data=[]):
        self.columns = columns
        self.data = data
        
        
    def __getitem__(self,key):
        if key=='columns':
            return self.columns
        
        if key=='data':
            return self.data
        
        
        
    def fieldIndex(self,name):
        return self.columns.index(name)
        
    
    def __repr__(self):
      
        #if len(self.data)>0:
         #   line=self.data[0]
       # else:
          #  line=''
        line = str(self.data)
            
        return 'table({cols}) \n{line}\n...'.format(cols=str(self.columns),line=line)
        
    
    
    def addRow(self,row):
        
        if any(isinstance(x, list) for x in row):
            raise TypeError('addRow element contained list')
        
        if any(isinstance(x, tuple) for x in row):
            raise TypeError('addRow element contained tuple')

        if len(row)!=len(self.columns):
            raise ValueError('addRow recieved wrong length row')

        self.data.append(row)
    
    
# from psycopyg2 cursor
def fromCur(cur):
    return table(columns = [desc[0] for desc in cur.description],data = [r for r in cur.fetchall()])


