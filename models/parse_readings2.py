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
def parseReadings(uri,run,dist=1):
    
    with open(uri,'r',encoding='utf-8',errors='ignore') as f:
        pos = 0
        lastVect = None
        
        for i,line in enumerate(f.readlines()):
            r = parseRow(line)
            if r is not None:
                
                if checkVect(r[3]):
                    yield {'s_ch':pos*0.1,#100m interval
                    'e_ch':(pos+1)*0.1,
                    'f_line':i,
                    'raw_ch':r[0],
                    't':r[1],
                    'rl':r[2],
                    'vect':r[3]}
                    
                pos += 1
                lastVect = r[3]
                
                #add extra run chainage where gap in readings.
                if lastVect is not None:
                    if lastVect.distance(r[3])>dist:
                        pos+=1


def test():
    uri = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\hsrr_processor\tests\A69_example\data\EB CL1\A69 DBFO EB CL1.xls'
    for r in parseReadings(uri,'test_run'):
        print(r)
        
        
if __name__ =='__console__':
    test()
        
#transformer = Transformer.from_crs(CRS.from_epsg(4326),CRS.from_epsg(27700))
#print(transformer.transform(-2.88659, 54.895925))