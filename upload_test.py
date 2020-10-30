import psycopg2

import io

#read line of hsrr spreadsheet. returns dict
def read_line(line,f_line,run):
    row=line.strip().split('\t')
    if is_valid(row):
        return {'raw_ch':float(row[0])*1000,'ts':row[1],'rl':row[2],'start_lon':row[12],'start_lat':row[13],'end_lon':row[14],'end_lat':row[15],'f_line':f_line,'run':run}


#check row of hsrr spreadsheet
def is_valid(row):
    if len(row)>=15 and row[0]!='Position km':
        return row[0] and row[1] and row[2]  and row[12] and row[13] and row[14] and row[15]


def parse_line(line,f_line,run):
    row=line.strip().split('\t')
    if is_valid(row):
        return ','.join([row[0],row[1],row[2],row[12],row[13],row[14],row[15],str(f_line),run])
    




f=r'L:\SharedDocs\Job Files 2020\2023-06-Bracknell Pavement Investigation\Data\HSRR\Bracknell\A Roads\A321 TO CIRCLE HILL SB C\A321 TO CIRCLE HILL C OPPOSITE.xls'
ref='A321 TO CIRCLE HILL C OPPOSITE'

csv_like = io.StringIO()
#csv_like.write()


with open(f,'r',encoding='utf-8',errors='ignore') as d:
    lines=[parse_line(line,i+1,ref) for i,line in enumerate(d.readlines())]
    [csv_like.write(line+'\n') for line in lines if line]
    

csv_like.seek(0)

    
table='hsrr.staging'


con=psycopg2.connect(host='192.168.5.157',dbname='pts2023_06_bracknell_hsrr',user='stuart')
cur=con.cursor()
with con:
    cur.copy_from(csv_like,table,sep=',',columns=['raw_ch','ts','rl','start_lon','start_lat','end_lon','end_lat','f_line','run'])
