# -*- coding: utf-8 -*-

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


            

def isHeaderRow(row):
    if row==['position km', 'date / time', 'rl', 'rl min', 'rl max', 'rl std dev', 'rl % pass', 'marker', 'temperature c', 'humidity rh', 'speed km/h', 'reference', 'gps long start', 'gps lat start', 'gps long', 'gps lat', 'files']:
        return True

    #if all(x in list_1 for x in list_2)


#doesn't currently use header. could potentially use to get column positions?
#row is list of tab seperated
def parseRow(row,header,lineNumber,startLineNumber,run):
    return {'raw_ch':row[0],'t':row[1],'rl':row[2],'start_lon':row[12],'start_lat':row[13],
            'end_lon':row[14],'end_lat':row[15],'f_line':lineNumber,
            'line':lineNumber-startLineNumber,'run':run}


#generator yielding rows after header row as dict
#won't return anything if no headerRow
def parseReadings(uri,run):
    
    with open(uri,'r',encoding='utf-8',errors='ignore') as f:
        
        header = None
        startLineNumber = None
        
        for i,line in enumerate(f.readlines()):
            
            row = line.lower().strip().split('\t')
            
            if not header is None:
                r = parseRow(row,header,i,startLineNumber,run)
                if r['start_lon']!=0 and r['start_lat']!=0:#remove 0,0 readings. faulty gps.
                    yield r
            
            if isHeaderRow(row):
                header = row
                startLineNumber = i+1
            
           

def isReadings(uri):
    for r in parseReadings(uri,''):
        if r:
            return True
    return False
    

def test():
    uri = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\hsrr_processor\tests\example_data\SEW NB CL1.xls'
    #uri = r'C:\Users\drew.bennett\Documents\hsrr_test\example_data\other.xls'

    for r in parseReadings(uri,'test_run'):
        print(r)
    #print(isReadings(uri))
    
    
    
if __name__ =='__main__':
    test()
    