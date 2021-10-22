
import psycopg2
from PyQt5.QtWidgets import QUndoCommand





'''
data:list like of dict like [{}]
need same keys for every row

returning: list like of columns to return
returns cur.fetchall()
should probaly look into sql injection...
'''

def insert(cur,table,data,returning=''):
    
    if returning:
        returning ='returning '+','.join(returning)    
    
    columns = list(data[0].keys())
        
    a = ','.join(['%('+col+')s' for col in columns ])   # eg  %(run)s,%(sec)s
    vals = ','.join([cur.mogrify("("+a+")",row).decode() for row in data])
           
    q = "insert into {table} ({columns}) VALUES {vals} {returning};"
    q = q.format(table=table,columns=','.join(columns),vals=vals,returning=returning)
    cur.execute(q)
    return cur.fetchall()
    #    return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())


'''
#use dictcursor to get data suitable to use with insert
pks: list like of dict like. deletes where key=value and key2=value2...
'''
def delete(cur,table,pks,returning=''):
    if returning:
        if isinstance(returning,list):
            returning ='returning '+','.join(returning)
        else:
            returning = 'returning ' + returning
        
   # '(a=b and c=d) or ()'...
    condition= ' or '.join([rowCondition(pk) for pk in pks])
        
    q = 'delete from {table} where {condition} {returning}'
    q = q.format(table=table,condition=condition,returning=returning)
    cur.execute(q)
    return cur.fetchall()


def rowCondition(pk):
    return '('+' and '.join([k+'='+str(pk[k]) for k in pk])+')'
    

data = [{'run':'SEW NB CL1','sec':'D','ch':-110},{'run':'SEW NB CL1','sec':'D','ch':-10}]
pks = [{'pk':557},{'pk':558}]

with psycopg2.connect(host='localHost',dbname='test',user='postgres') as con:
    cur = con.cursor()
    
    print(delete(cur,'hsrr.section_changes',pks,'*'))
   