import sys

import psycopg2

import logging
logger = logging.getLogger(__name__)


if __name__ =='__console__':
    d = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\hsrrprocessor'
    sys.path.insert(0,d)
    

from . import parseReadings
#import parseReadings

#from itertools import chain


class readingsModel:
    
    def __init__(self,db):
        self.db = db
               
    def con(self):
        db = self.db
        return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())
    
    
    
    #parse .xls file and insert into readings table. Need to insert into run_info before calling this.
    def uploadXls(self,uri,run):
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
            #cur.execute('update hsrr.readings set s_ch = (f_line-(select min(f_line) from hsrr.readings as r where r.run=readings.run))*0.1 where run=%(run)s;',{'run':run})#s_ch in km
          #  cur.execute('update hsrr.readings set e_ch=s_ch+0.1 where run=%(run)s;',{'run':run})#s_ch in km
        
        
        
        
    def dropRuns(self,runs):
         with self.con() as con:
            cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute('delete from hsrr.readings where run = any(%(runs)s) returning run,f_line,t,raw_ch,rl,st_asText(vect) as vect,s_ch,e_ch',{'runs':runs})
            return [dict(r) for r in cur.fetchall()]
        
        
        
    #like [{}] takes result of dropRuns
    def uploadDicts(self,data):
        logger.info('uploadDicts()',data)
        with self.con() as con:
        
            q = '''
            insert into hsrr.readings(run,f_line,t,raw_ch,rl,vect,s_ch,e_ch) values (
                %(run)s,%(f_line)s,%(t)s,%(raw_ch)s,%(rl)s
                ,ST_SetSRID(ST_GeomFromText(%(vect)s),27700))
                ,%(s_ch)s
                ,%(e_ch)s
            '''
            cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            psycopg2.extras.execute_batch(cur,q,data)
           
            
            

    #doesn't work in spyder. db.isValid() False   
if __name__=='__main__' or __name__ =='__console__':
    
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
                
            