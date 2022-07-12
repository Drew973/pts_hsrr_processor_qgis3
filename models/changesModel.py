
from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtWidgets import QUndoStack
from PyQt5.QtCore import Qt
from qgis.core import QgsCoordinateReferenceSystem


import logging
logger = logging.getLogger(__name__)


import psycopg2
import psycopg2.extras#not always imported with import psycopyg2. version dependent.


#from hsrr_processor.undo_commands.commands import multiUpdateCommand,pairedFunctionCommand,functionCommand
from hsrr_processor.functions import layer_functions


from hsrr_processor.models import commands




'''
    model with routes table.
    undoable:
        -setData
        -insertRows
        -dropRows
    

'''


class changesModel(QSqlTableModel):

    
#db=qsqldatabase
    def __init__(self,db,undoStack=QUndoStack(),parent=None):
        super().__init__(parent=parent,db=db)
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
       
        self.setTable('hsrr.routes')
        self.hiddenColIndexes = [self.fieldIndex(col) for col in ['run','pk']]#needs to be after setTable

        self.setRun('')
        self.undoStack = undoStack
    


    def fieldIndex(self,name):
        return self.record().indexOf(name)
        


    def fieldName(self,column):
        return self.record().fieldName(column)
        


    def getCrs(self):
        return QgsCoordinateReferenceSystem(27700)



    def con(self):
        db = self.database()
        try:
            return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())   
        except:
            return None



    def setRun(self,run):
        self._run = run
        
        f = "run = '{run}' order by start_run_ch, NULLIF( sec,'D') NULLS FIRST".format(run=run)#start_run_ch,dummys,other sections
        self.setFilter(f)
        self.select()
   


    def run(self):
        return self._run



    def _setData(self,index,value):
        return super().setData(index,value,Qt.EditRole)
    
    

    def setData(self, index, value, role=Qt.EditRole):
        if role==Qt.EditRole:
            self.undoStack.push(commands.updateCommand(index=index,value=value))
        else:
            super().setData(index, value, role)

        
        
    def pk(self,index):
        return index.sibling(index.row(),self.fieldIndex('pk')).data()
                
        
        
    def undo(self):
        self.undoStack.undo()



    def redo(self):
        self.undoStack.redo()        
        
        
        
    def setReadingsModel(self,model):
        self._readingsModel = model
        
        
    
    def XYToFloat(self,x,y,index):
        c = index.column()
    
        if c == self.fieldIndex('start_sec_ch') or c == self.fieldIndex('end_sec_ch'):
            return self._networkModel.XYToChainage(x,y,self.sectionLabel(index))#x,y,sec
    
        if c == self.fieldIndex('ch') or c == self.fieldIndex('e_ch'):
            return self._readingsModel.XYToChainage(x,y)
    
   
    
    def floatToXY(self,value,index):
        c = index.column()
    
        if c == self.fieldIndex('start_sec_ch') or c == self.fieldIndex('end_sec_ch'):
            return self._networkModel.chainageToXY(value,self.sectionLabel(index))#x,y,sec
        
        if c==self.fieldIndex('ch'):
            return self._readingsModel.chainageToXY(value,True)
    
        if c==self.fieldIndex('e_ch'):
            return self._readingsModel.chainageToXY(value,False)
    


    def minValue(self,index):
        c = index.column()
        if c==self.fieldIndex('ch') or c==self.fieldIndex('e_ch'):
            return self._readingsModel.minValue()
            
    
    
    def maxValue(self,index):
        c = index.column()
        if c==self.fieldIndex('ch') or c==self.fieldIndex('e_ch'):
            return self._readingsModel.maxValue()
    
   
    
    def setNetworkModel(self,model):
        self._networkModel = model
    
    
    
    def networkModel(self):
        return self._networkModel
    
    
    
    def dropRuns(self,runs):
        self.undoStack.push(commands.dropRunsCommand(model=self,runs=runs))  
        
        
    
    #remove runs from routes table and return deleted data.
    def _dropRuns(self,runs):
        with self.con() as con:
            cur = con.cursor()
            cur.execute('delete from hsrr.routes where run = any(%(runs)s) returning run,start_run_ch,end_run_ch,note,sec,start_sec_ch,end_sec_ch,xsp,pk',{'runs':runs})
            
            if self.run() in runs:
                self.setRun(None)            
            
            return [r for r in cur.fetchall()]



    def insertRow(self,run='',start_run_ch=0,end_run_ch=0,note='',sec='D',start_sec_ch=0,end_sec_ch=0,xsp='',pk=None):
        
        if not run:
            run = self.run()
        
        if pk is None:
            self.insertRows([(run,start_run_ch,end_run_ch,note,sec,start_sec_ch,end_sec_ch,xsp)])
        else:
            self.insertRows([(run,start_run_ch,end_run_ch,note,sec,start_sec_ch,end_sec_ch,xsp,pk)])


        
    def insertRows(self,data):
        self.undoStack.push(commands.insertCommand(model=self,data=data))        

        
        
    #data like [(run,start_run_ch,end_run_ch,note,sec,start_sec_ch,end_sec_ch,xsp,pk),...]
    #returns pk of new row.
    #can leave pk as 'DEFAULT'
    def _insertRows(self,data):
        #run,sec,xsp,ch,note,start_sec_ch,end_sec_ch,pk
        logger.debug('_insertRows:'+str(data))
        r = []
        
        if data:
            if len(data)>0:
                
                if len(data[0])==8:
                    cols = ['run','start_run_ch','end_run_ch','note','sec','start_sec_ch','end_sec_ch','xsp']          
                    
                if len(data[0])==9:
                    cols = ['run','start_run_ch','end_run_ch','note','sec','start_sec_ch','end_sec_ch','xsp','pk']          
                
                q = '''insert into hsrr.routes({cols})
                values %s
                returning pk
                    '''.format(cols=','.join(cols))
                    #ok to do this here as not user editable
        
                with self.con() as con:
                
                    if con is not None:
                        cur = con.cursor()            
                        r = psycopg2.extras.execute_values(cur,q,data,fetch=True)
                self.select()#select after commiting changes
        return r
        
    
    
    #rows = list of model rows.
    def dropRows(self,rows):
        col = self.fieldIndex('pk')
        pks = [self.index(r,col).data() for r in rows]#get primary keys.
        logger.debug(pks)
        self.undoStack.push(commands.dropCommand(model=self,pks=pks))

    
    
    def _dropRows(self,pks):
        logger.debug('_dropRows:'+str(pks))
        
        q = 'delete from hsrr.routes where pk = any(%(pks)s) returning run,start_run_ch,end_run_ch,note,sec,start_sec_ch,end_sec_ch,xsp,pk'
        
        
        data = []
        with self.con() as con:
                
            if con is not None:
                cur = con.cursor()            
                cur.execute(q,{'pks':pks})
                data = [r for r in cur.fetchall()]
                
                
        self.select()#select after commiting changes
        return data
    
    

    #execute_batch can return results in psycopg2 >=2.8
    #autofit run, returning primary keys of new rows
    def topologyAutofit(self,arg=None):
        logger.info('topologyAutofit(),run %s'%(self.run))
        if not self.run is None:
            with self.con() as con:
                cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute('select pk from hsrr.topology_based_autofit(%(run)s)',{'run':self.run})
                res = [dict(r) for r in cur.fetchall()]
            self.select()
            return res



    def runQuery(self,query,args):
        con = self.con()
        if con is not None:
            cur = con.cursor()
            cur.execute(query,args)
            r = [r for r in cur.fetchall()]
            con.commit()
            return r



    def sequencialScoreAutofit(self):
        pass
        #self.undoStack.push(pairedFunctionCommand(function = self._sequencialScoreAutofit,inverseFunction=self._dropRows,description='sequencialScoreAutofit'))



    def simpleAutofit(self):
        pass
        #self.undoStack.push(pairedFunctionCommand(function = self._simpleAutofit,inverseFunction=self._dropRows,description='sequencialScoreAutofit'))



    def filteredAutofit(self):
        pass
        #self.undoStack.push(pairedFunctionCommand(function = self._filteredAutofit,inverseFunction=self._dropRows,description='filteredAutofit'))



    def _filteredAutofit(self):
        if self.run is not None:
           r = {'pks':self.runQuery('select pk from hsrr.filtered_autofit(%(run)s)', {'run': self.run()})}
           self.select()
           return r
       
        

    def _simpleAutofit(self):
      #  print('_sequencialScoreAutofit',self.run)
        if self.run is not None:
           r = {'pks':self.runQuery('select pk from hsrr.simple_autofit(%(run)s)', {'run': self.run()})}
           self.select()
           return r
        
        

    def _sequencialScoreAutofit(self):
      #  print('_sequencialScoreAutofit',self.run)
        if self.run is not None:
           r = {'pks':self.runQuery('select pk from hsrr.filtered_autofit(%(run)s)', {'run': self.run()})}
           self.select()
           return r
   
    
    def leastCostAutofit(self):
        pass
        #self.undoStack.push(pairedFunctionCommand(function = self._leastCostAutofit,inverseFunction=self._dropRows,description='least cost autofit'))

    
   
    def _leastCostAutofit(self):
      #  print('_sequencialScoreAutofit',self.run)
        if self.run is not None:
           r = {'pks':self.runQuery('select pk from hsrr.least_cost_autofit(%(run)s)', {'run': self.run()})}
           self.select()
           return r

#returns command to set xsp
    def setXspCommand(self,xsp,description='set xsp'):
        #col = self.fieldIndex('xsp')
        pass
        #return multiUpdateCommand(data={self.index(row,col):xsp for row in range(self.rowCount())},description=description)



    def sectionLabels(self,rows):
        col = self.fieldIndex('sec')
        return [self.index(r,col).data() for r in rows]



    def sectionLabel(self,index):
        col = self.fieldIndex('sec')
        return self.index(index.row(),col).data()
    
    
    
    #list of turples [(start,end)] for rows
    def runChainages(self,rows):
        sCol = self.fieldIndex('ch')
        eCol = self.fieldIndex('e_ch')
        return [(self.index(row,sCol).data(),self.index(row,eCol).data()) for row in rows]



#run query and get result of 1st line
    def singleLineQuery(self, query,args):
        c = self.con()
        if c is not None:
            cur = c.cursor()
            cur.execute(query,args)
            return cur.fetchone()



    def selectOnLayers(self,rows):        
        self._networkModel.selectSectionsOnlayer(self.sectionLabels(rows))
        self._readingsModel.selectOnLayer(self.runChainages(rows))
        layer_functions.zoomToFeatures(self._networkModel.selectedFeatures()+self._readingsModel.selectedFeatures())
        
