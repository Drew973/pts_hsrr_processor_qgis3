import os 
import psycopg2


import logging
logger = logging.getLogger(__name__)


'''
run ';' seperated list of files consecutively.
files relative paths from setup script
'''

def runSetupFile(cur,file):
    folder = os.path.dirname(file) 

    with open(file) as f:
        
        for c in f.read().split(';'):
            logger.info(c)
            if c:
                runScript(cur,os.path.join(folder,c.strip()))
                    
              
                        
 
# QSqlDatabase to psycopg2 connection
def dbToCon(db):
    return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password()) 
 
 
 

def runScript(cur,script,args={}):
        s = script
        
        if os.path.dirname(script)=='':
            s = os.path.join(os.path.dirname(__file__),script)
    
        with open(s,'r') as f:
            if args:
                cur.execute(f.read(),args)
            else:
                cur.execute(f.read())
                
          