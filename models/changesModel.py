
from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtWidgets import QUndoStack
from PyQt5.QtCore import Qt
from qgis.core import QgsCoordinateReferenceSystem


import logging
logger = logging.getLogger(__name__)


import psycopg2
import psycopg2.extras#not always imported with import psycopyg2. version dependent.


from hsrr_processor.undo_commands.commands import multiUpdateCommand,pairedFunctionCommand,functionCommand
from hsrr_processor.functions import layer_functions



class changesModel(QSqlTableModel):
#class changesModel(QSqlRelationalTableModel):

    
#db=qsqldatabase
    def __init__(self,db,undoStack=QUndoStack(),parent=None):
        super().__init__(parent=parent,db=db)
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
       
        self.setTable('hsrr.section_changes')
        self.hiddenColIndexes = [self.fieldIndex(col) for col in ['run','pk','pt','reversed']]#needs to be after setTable

        self.setRun('')
        self.undoStack = undoStack
    


    def fieldIndex(self,name):
        return self.record().indexOf(name)


    def row(self,pk):
        col = self.fieldIndex('pk')
        for i in range(self.rowCount()):
            if self.index(i,col).data() == pk:
                return i
        return -1
        


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
        
        f = "run = '{run}' order by ch, NULLIF( sec,'D') NULLS FIRST".format(run=run)
        self.setFilter(f)
        self.select()
   


    def run(self):
        return self._run



#pk = primary key
#col: int
#value: any QVariant
    def _update(self,pk,col,value):
        r = self.row(pk)
        return super().setData(self.index(r,col),value,Qt.EditRole)
    
    

    def setData(self, index, value, role=Qt.EditRole):
        if role==Qt.EditRole:
            pk = self.pk(index)
            c = functionCommand(self._update,
                                {'pk':pk,'col':index.column(), 'value':value},
                                self._update,
                                {'pk':pk,'col':index.column(), 'value':index.data()}
                                ,'setData'
                                )
            self.undoStack.push(c)
            return c.result #self._update(pk, index.column(), value)

        else:
            super().setData(index, value, role)

        
        
    def pk(self,index):
        print('pk:',index.row(),self.fieldIndex('pk'))
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
        with self.con() as con:
            cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute('delete from hsrr.section_changes where run = any(%(runs)s) returning run,sec,reversed,xsp,ch,note,start_sec_ch,end_sec_ch',{'runs':runs})
            return [dict(r) for r in cur.fetchall()]
    
            
    
    def insertRow(self,sec='D',xsp='',ch=0,note='',startSecCh=0,endSecCh=0):
        #data = [{'run':self.run,'sec':sec,'xsp':xsp,'ch':ch,'note':note,'startSecCh':startSecCh,'endSecCh':endSecCh}]
        data = [(self.run(),sec,xsp,ch,note,startSecCh,endSecCh)]
        print('changesModel.insertData',data)
        self.undoStack.push(pairedFunctionCommand(function = self._insertRows,inverseFunction=self._dropRows,description='insert row',data=data))
    
    
        
        
    #data like [{'pk':pk,'run':'run','sec':'','xsp':'','ch':'','note':'','startSecCh':'','endSecCh':''},...]
    #returns pk of new row.
    #can leave pk as 'DEFAULT'
    def _insertRows(self,data):
        #run,sec,xsp,ch,note,start_sec_ch,end_sec_ch,pk
        
        if len(data[0])==7:
            cols = ['run','sec','xsp','ch','note','start_sec_ch','end_sec_ch']
            
        if len(data[0])==8:
            cols = ['run','sec','xsp','ch','note','start_sec_ch','end_sec_ch','pk']          
        
        
        q = '''insert into hsrr.section_changes({cols})
        values %s
        returning pk
            '''.format(cols=','.join(cols))
            #ok to do this here as not user editable

            
        con = self.con()
        
        if con is not None:
            cur = con.cursor()            
            r = {'pks':psycopg2.extras.execute_values(cur,q,data,fetch=True)}
            con.commit()
            self.select()
            return r
        
        
    
    #model index
    def dropRows(self,rows):
        c = self.fieldIndex('pk')
        pks = [self.index(r,c).data() for r in rows]
        self.undoStack.push(pairedFunctionCommand(function = self._dropRows,inverseFunction=self._insertRows,description='drop rows',pks=pks))

    
    
    def _dropRows(self,pks):
        q = 'delete from hsrr.section_changes where pk = any(%(pks)s) returning run,sec,xsp,ch,note,start_sec_ch,end_sec_ch,pk'
        r = {'data':self.runQuery(q,{'pks':pks})}
        self.select()
        return r
    
    

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
        self.undoStack.push(pairedFunctionCommand(function = self._sequencialScoreAutofit,inverseFunction=self._dropRows,description='sequencialScoreAutofit'))



    def simpleAutofit(self):
        self.undoStack.push(pairedFunctionCommand(function = self._simpleAutofit,inverseFunction=self._dropRows,description='sequencialScoreAutofit'))



    def filteredAutofit(self):
        self.undoStack.push(pairedFunctionCommand(function = self._filteredAutofit,inverseFunction=self._dropRows,description='filteredAutofit'))



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
        self.undoStack.push(pairedFunctionCommand(function = self._leastCostAutofit,inverseFunction=self._dropRows,description='least cost autofit'))

    
   
    def _leastCostAutofit(self):
      #  print('_sequencialScoreAutofit',self.run)
        if self.run is not None:
           r = {'pks':self.runQuery('select pk from hsrr.least_cost_autofit(%(run)s)', {'run': self.run()})}
           self.select()
           return r

#returns command to set xsp
    def setXspCommand(self,xsp,description='set xsp'):
        col = self.fieldIndex('xsp')
        return multiUpdateCommand(data={self.index(row,col):xsp for row in range(self.rowCount())},description=description)



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
        
