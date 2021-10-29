
import psycopg2

import logging
logger = logging.getLogger(__name__)



from . import parseReadings
#import parseReadings

#from itertools import chain


class readingsModel:
    
    def __init__(self,db):
        self.db = db
               
    def con(self):
        db = self.db
        return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())
    
    
    
    #parse single .xls file and insert into readings table. Need to insert into run_info before calling this.
    def uploadXls(self,uri,run):
        logger.info('uploadXls(%s,%s)'%(str(uri),str(run)))
        with self.con() as con:
            cur = con.cursor()
            
            q = '''
            insert into hsrr.readings(run,f_line,t,raw_ch,rl,vect,s_ch,e_ch)
            values(
            %(run)s
            ,%(f_line)s
            ,to_timestamp(replace(%(t)s,' ',''),'dd/mm/yyyyHH24:MI:ss')
            ,%(raw_ch)s
            ,%(rl)s
            ,ST_MakeLine(St_Transform(ST_SetSRID(ST_makePoint(%(start_lon)s,%(start_lat)s),4326),27700),St_Transform(ST_SetSRID(ST_makePoint(%(end_lon)s,%(end_lat)s),4326),27700))	
            ,%(line)s * 0.1
            ,%(line)s * 0.1 +0.1
            )
            '''
            psycopg2.extras.execute_batch(cur,q,parseReadings.parseReadings(uri,run))
        
        
        
    def dropRuns(self,runs):
        logger.info('dropRuns(%s)'%(str(runs)))
        with self.con() as con:
            cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute('delete from hsrr.readings where run = any(%(runs)s) returning run,f_line,t,raw_ch,rl,st_asText(vect) as vect,s_ch',{'runs':runs})
            return [dict(r) for r in cur.fetchall()]
     
     #storing all readings prevents them being lost if run_info.file wrong.
     #but uses lots of memory
     
        
        
    #like [{}] takes result of dropRuns
    def uploadDicts(self,data):
        logger.info('uploadDicts(%s)'%(str(data)))
        with self.con() as con:
        
            q = '''
            insert into hsrr.readings(run,f_line,t,raw_ch,rl,vect,s_ch,e_ch) values (
                %(run)s,%(f_line)s,%(t)s,%(raw_ch)s,%(rl)s
                ,ST_SetSRID(ST_GeomFromText(%(vect)s),27700)
                ,%(s_ch)s
                ,%(s_ch)s + 0.1)
            '''
            cur = con.cursor()
            
            psycopg2.extras.execute_batch(cur,q,data)
           
            
            

    #doesn't work in spyder. db.isValid() False   
def test():
    
    from PyQt5.QtSql import QSqlDatabase
    
    
    db = QSqlDatabase.addDatabase("QPSQL")
   # db = QSqlDatabase('QPSQL')
    db.close()
    db.setHostName('localhost')
    db.setDatabaseName('test')
    db.setUserName('postgres')
    
    print(db.open())
    
    uri = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\hsrrprocessor\test\example_data\SEW NB CL1.xls'
    m = readingsModel(db)
    m.uploadXls(uri,'A1M NB RE')
    
    print('uploaded')
                
            