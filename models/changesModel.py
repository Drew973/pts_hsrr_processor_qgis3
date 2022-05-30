#from qgis.PyQt.QtCore import Qt
#from . better_table_model import  

from PyQt5.QtSql import QSqlTableModel#,QSqlRelationalTableModel,QSqlRelation
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QUndoStack


import logging
logger = logging.getLogger(__name__)


import psycopg2
import psycopg2.extras#not always imported with import psycopyg2. version dependent.

from hsrr_processor.models import undoableTableModel

from hsrr_processor.undo_commands.commands import multiUpdateCommand,pairedFunctionCommand
from hsrr_processor.functions import layer_functions


'''
editable qsqlQueryModel. Can properly set order by. 
'''



class changesModel(undoableTableModel.undoableTableModel):
#class changesModel(QSqlRelationalTableModel):

    
#db=qsqldatabase
    def __init__(self,db,undoStack=QUndoStack(),parent=None):
        super().__init__(parent=parent,db=db,undoStack=undoStack,autoIncrementingColumns=['pk','pt'])

        self.setTable('hsrr.section_changes') 
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.setSort(self.fieldIndex("ch"),Qt.AscendingOrder)#sort by s
        self.select()
        self.hiddenColIndexes=[self.fieldIndex(col) for col in ['run','pk','pt','reversed']]
        self.run = None
        self.undoStack = undoStack
    


    def con(self):
        db = self.database()
        try:
            return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())   
        except:
            return None



  #  def select(self):
   #     self.setQuery(self.query())



    def database(self):
        return self.query().database()




    def _setData(self,index,value):
        pass



   # def setData(self, index, value, role=Qt.EditRole):
    #    pass



    def setRun(self,run):
        logger.info('setRun(%s)'%(run))
        filt = "run='%s'"%(run)
        logger.info(filt)
        self.setFilter(filt)
        self.select()
        self.run = run
        
        
        
    def pk(self,index):
        return self.index(index.row(),self.fieldIndex('pk')).data()
                
        
        
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
        
    
        if c==self.fieldIndex('ch'):
            return self._readingsModel.XYToChainage(x,y)
    
   
    
    def floatToXY(self,value,index):
        c = index.column()
    
        if c == self.fieldIndex('start_sec_ch') or c == self.fieldIndex('end_sec_ch'):
            return self._networkModel.chainageToXY(value,self.sectionLabel(index))#x,y,sec
        
    
        if c==self.fieldIndex('ch'):
            return self._readingsModel.chainageToXY(value)
    
   
    
    def setNetworkModel(self,model):
        self._networkModel = model
    
    
    
    def networkModel(self):
        return self._networkModel
    
    
    
    def dropRuns(self,runs):
        with self.con() as con:
            cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute('delete from hsrr.section_changes where run = any(%(runs)s) returning run,sec,reversed,xsp,ch,note,start_sec_ch,end_sec_ch',{'runs':runs})
            return [dict(r) for r in cur.fetchall()]
    
            
        
   # #returns QundoCommand to drop primary keys pks
   # def dropCommand(self,pks,description=''):
    #    return methodCommand(self.drop,pks,self.insert,description)
            
    
    
    def insertRow(self,sec='D',xsp='',ch=0,note='',startSecCh=0,endSecCh=0):
        #data = [{'run':self.run,'sec':sec,'xsp':xsp,'ch':ch,'note':note,'startSecCh':startSecCh,'endSecCh':endSecCh}]
        data = [(self.run,sec,xsp,ch,note,startSecCh,endSecCh)]
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
    
        
        #print('dropRows',pks)
    #    con = self.con()
      #  if con is not None:
      #      q = 'delete from hsrr.section_changes where pk = any(%(pks)s) returning run,sec,xsp,ch,note,start_sec_ch,end_sec_ch'
      #      cur = con.cursor()
       #     cur.execute(q,{'pks':pks})
        #    self.select()
         #   return {'data':[r for r in cur.fetchall()]}
    
    

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



    def _simpleAutofit(self):
      #  print('_sequencialScoreAutofit',self.run)
        if self.run is not None:
           r = {'pks':self.runQuery('select pk from hsrr.simple_autofit(%(run)s)', {'run': self.run})}
           self.select()
           return r
        
        

    def _sequencialScoreAutofit(self):
      #  print('_sequencialScoreAutofit',self.run)
        if self.run is not None:
           r = {'pks':self.runQuery('select pk from hsrr.filtered_autofit(%(run)s)', {'run': self.run})}
           self.select()
           return r



    def filteredAutofit(self,arg=None):
        logger.info('sequencialScoreAutofit(),run %s' % (self.run))
        if self.run is not None:
            with self.con() as con:
                cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute('select pk from hsrr.filtered_autofit(%(run)s)', {'run': self.run})
                res = [dict(r) for r in cur.fetchall()]
            self.select()
            return res



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
    
    

    def runChainages(self,rows):
        return [self.runChainage(r) for r in rows]



    def runChainage(self,row):
        col = self.fieldIndex('ch')
        s = self.index(row,col).data()
        e = self.index(row+1,col).data()
        return (s,e)



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
        
