import os 

import logging
logger = logging.getLogger(__name__)


import psycopg2



def dbToCon(db):
    return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password()) 
 


def runScript(cur,script):
    with open(script) as f:
        c = f.read()
        logger.debug(c)
        print(c)
        cur.execute(c)




'''
runs ';' seperated list of scripts in setup.txt on QSqlDatabase.
through psycopg2.
QSqlQuery would be more elegent and database independent 
but big problems as can only run 1 command at time and some commands contain ';' 
(unavoidable for user defined functions)
user defined functions are postgres specific.


'''
def setupDb(db):

    try:
        file = os.path.join(os.path.dirname(__file__),'setup.txt')
        logger.debug(file)

        folder = os.path.dirname(file)
        
        
        with dbToCon(db) as con:
            cur = con.cursor()

            with open(file) as f:
                
                for c in f.read().split(';'):
                    s = c.strip()                
                    if s:
                        logger.debug(s)
                        print(s)
                        s = os.path.join(folder,s)
                        runScript(cur,s)
                        
        return True
    
    except Exception as e:
        return e

