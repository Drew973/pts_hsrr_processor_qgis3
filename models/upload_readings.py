# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 09:21:44 2022

@author: Drew.Bennett
"""


from datetime import datetime
from qgis.core import QgsPointXY,QgsGeometry,QgsProject,QgsCoordinateReferenceSystem,QgsCoordinateTransform


#only returns results if valid
#returns for rows with no gps (0,0)

transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:4326"),
                                   QgsCoordinateReferenceSystem("EPSG:27700"), QgsProject.instance())


def parseRow(row):
   
    try:
        row = row.lower().strip().split('\t')
                     
        g= QgsGeometry.fromPolylineXY([ QgsPointXY(float(row[12]),float(row[13])),QgsPointXY(float(row[14]),float(row[15]))])
        g.transform(transform)

        return [float(row[0]),#'raw_ch'
                datetime.strptime(row[1],r'%d/%m/%Y  %H:%M:%S'),#'timestamp'
                float(row[2]),#rl
                g#geometry
               ]
    
    except Exception as e:
        return


#check geometry of row.
def checkVect(g):
    return 0<g.length() and g.length()<200 #geometry should be 0-200m long
        
    
    
#generator yielding rows after header row as dict
#won't return anything if no headerRow

#add 0.1 to start_ch and end_ch after gap.



def parseReadings(uri,run,dist=1):
    
    with open(uri,'r',encoding='utf-8',errors='ignore') as f:
        pos = 0
        lastVect = None
        
        for i,line in enumerate(f.readlines()):
            r = parseRow(line)
            if r is not None:
                
                if checkVect(r[3]):
                    
                    #add extra run chainage where gap in readings.
                    if lastVect is not None:
                       # print(lastVect.distance(r[3]))
                        if lastVect.distance(r[3])>dist:
                            #print('gap')
                            pos+=1
                            
                    lastVect = r[3]
                    
                    yield {'run':run,
                    's_ch':pos*0.1,#100m interval
                    'e_ch':(pos+1)*0.1,
                    'f_line':i,
                    'raw_ch':r[0],
                    't':r[1],
                    'rl':r[2],
                    'vect':r[3].asWkt()}
                    
         
                    
                pos += 1
                

import psycopg2
from hsrr_processor.tests import get_db

def loadSpreadSheet(db,spreadsheet,runName):
    with psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password()) as con:

            cur = con.cursor()
                
            q = '''
                insert into hsrr.readings(run,f_line,t,raw_ch,rl,vect,s_ch,e_ch)
                values(
                %(run)s
                ,%(f_line)s
                ,%(t)s
                ,%(raw_ch)s
                ,%(rl)s
                ,%(vect)s	
                ,%(s_ch)s
                ,%(e_ch)s
                )
            '''
            psycopg2.extras.execute_batch(cur,q,parseReadings(uri=spreadsheet,run=runName)) 



def test():
   # uri = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\hsrr_processor\tests\A69_example\data\EB CL1\A69 DBFO EB CL1.xls'
    uri = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\hsrr_processor\tests\A69_example\data\SLIPS\EB CL1\A69 DBFO EB CL1.xls'
    for r in parseReadings(uri,'test_run'):
        if 0.7<r['s_ch'] and r['s_ch']<1.1:
            print(r)
        
        
def testLoad():
    uri = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\hsrr_processor\tests\A69_example\data\SLIPS\EB CL1\A69 DBFO EB CL1.xls'
    db =  get_db.getDb()
    loadSpreadSheet(db,uri,'test_run')
        
if __name__ =='__console__':
    testLoad()
        




