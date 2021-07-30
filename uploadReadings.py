# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
import os



'''
readings files have .xls extention BUT ARE NOT .xls FORMAT.

tab seperated csv with extra rows at top.



test if file valid with headerRow()


Position km 
raw_ch
date/time
RL
gps Long start
gps lat start
gps long
gps lat

'''


COLS = []


#dict of name:col+'startRow':startRow from readings file
#returns None if file is not readings file

def headerRow(uri):
    with open(uri,'r',encoding='utf-8',errors='ignore') as f:
        i = 0
        for line in f.readlines():
            i+=1
            row = line.lower().strip().split('\t')
            if isHeaderRow(row):
                return {'startRow':i}
            

def isHeaderRow(row):
    if row==['position km', 'date / time', 'rl', 'rl min', 'rl max', 'rl std dev', 'rl % pass', 'marker', 'temperature c', 'humidity rh', 'speed km/h', 'reference', 'gps long start', 'gps lat start', 'gps long', 'gps lat', 'files']:
        return True

    #if all(x in list_1 for x in list_2)


def parseRow(row,header,f_line,run):
    return {'raw_ch':row[0],'t':row[1],'rl':row[2],'start_lon':row[12],'start_lat':row[13],'end_lon':row[14],'end_lat':row[15],'f_line':f_line,'run':run}
    #return ','.join([row[0],row[1],row[2],row[12],row[13],row[14],row[15],str(f_line),run])


#generator yielding rows as dict
#use header to get column order?
def parseReadings(uri,header,run):
    
    with open(uri,'r',encoding='utf-8',errors='ignore') as f:
        i = 0
        for line in f.readlines():
            row = line.lower().strip().split('\t')
            i+=1
            if i>header['startRow']:
                yield parseRow(row,header,i,run)
                

def uploadReadings(uri,con):

    header = headerRow(uri)
    if not header:
        raise ValueError('Header row not found. Check file format.')
    
    
    cur = con.cursor()
    cur.execute('insert into hsrr.run_info(run,file) values (hsrr.generate_run_name(%(prefered)s),%(uri)s)',
                {'prefered':os.path.splitext(os.path.basename(uri))[0],'uri':uri})
    
    cur.execute('select run from hsrr.run_info where file=%(uri)s',{'uri':uri})#file is unique
    
    run = cur.fetchall()[0][0]
   
    q = '''
            insert into hsrr.readings(run,f_line,t,raw_ch,rl,vect)
            values(
            %(run)s
            ,%(f_line)s
            ,to_timestamp(replace(%(t)s,' ',''),'dd/mm/yyyyHH24:MI:ss')
            ,%(raw_ch)s
            ,%(rl)s
            ,ST_MakeLine(St_Transform(ST_SetSRID(ST_makePoint(%(start_lon)s,%(start_lat)s),4326),27700),St_Transform(ST_SetSRID(ST_makePoint(%(end_lon)s,%(end_lat)s),4326),27700))	
            )
        '''
    
    psycopg2.extras.execute_batch(cur,q,parseReadings(uri,header,run))
    cur.execute('update hsrr.readings set s_ch = (f_line-(select min(f_line) from hsrr.readings as r where r.run=readings.run))*0.1 where run=%(run)s;',{'run':run})#s_ch in km
    cur.execute('update hsrr.readings set e_ch=s_ch+0.1 where run=%(run)s;',{'run':run})#s_ch in km
    
    
if __name__=='__main__':
    uri = r'C:/Users/drew.bennett/Documents/hsrr_test/SEW NB CL1.xls'
    con = psycopg2.connect(host='localhost',dbname='hsrr_test',user='postgres')
    uploadReadings(uri,con)
    con.commit()
    con.close()
    print('uploaded')
    
    