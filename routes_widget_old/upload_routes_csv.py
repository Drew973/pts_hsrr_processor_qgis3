from qgis.PyQt.QtSql import QSqlQuery

import psycopg2
from os import path


def upload_route(csv,con,table='routes'):
    with open(csv,'r') as f:
        c=con.cursor()        
        c.copy_from(f,table,sep=',')
        con.commit()
