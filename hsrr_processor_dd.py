from .database_dialog.database_interface import database_interface


import io
#import psycopg2
from qgis.PyQt.QtSql import QSqlQuery


import os


'''
subclass of database_interface specific to hsrr processor.

'''

class hsrr_dd(database_interface):

    def __init__(self,db):
        super().__init__(db)
        self.prefix='hsrr processor:'

#',' in note column is problem. fix with quote charactors?
    def upload_route(self,csv):
        with open(csv,'r') as f:
            with self.get_con() as con:
                if con:
                    con.cursor().copy_expert('copy hsrr.routes from STDIN with CSV HEADER',f)
            
#to is str
    def download_route(self,to,run):
        q="COPY (select * from hsrr.routes where run='%s') TO STDOUT WITH (FORMAT CSV,HEADER,FORCE_QUOTE(run,sec,note),null '')"%(run)
        with open(to,'w') as f:
            self.get_cur().copy_expert(q,f)
        

    def download_routes(self,to):
        with open(to,'w') as f:
            self.get_cur().copy_expert("COPY hsrr.routes TO STDOUT WITH (FORMAT CSV,HEADER,FORCE_QUOTE(run,sec,note),null '')",f)
        

    def remove_slips(self,run):
        self.sql('select hsrr.remove_slips(%(run)s)',{'run':run})
        

    def setup_database(self):
        f = os.path.join(os.path.dirname(__file__),'database')
        self.run_setup_file(folder=f,file='setup.txt')
      

    def autofit_run(self,run):
        self.sql('select hsrr.autofit_run(%(run)s)',{'run':run})


    def is_uploaded(self,file):
        r=self.sql('select run from hsrr.run_info where file=%(file)s;',{'file':file},ret=True)
       # print(r)
        if r:
            return True
        else:
            return False
    
    def upload_run_csv(self,f):
        try:
            ref=os.path.splitext(os.path.basename(f))[0]
            ref=self.generate_run_name(ref)
            csv_like = io.StringIO()

            with open(f,'r',encoding='utf-8',errors='ignore') as d:
                lines=[parse_line(line,i+1,ref) for i,line in enumerate(d.readlines())]
                [csv_like.write(line+'\n') for line in lines if line]
        
            csv_like.seek(0)

            with self.con:
                self.cur.copy_from(csv_like,table='hsrr.staging',sep=',',columns=['raw_ch','ts','rl','start_lon','start_lat','end_lon','end_lat','f_line','run'])

            self.sql('insert into hsrr.run_info(run,file) values(%(run)s,%(file)s);',{'run':ref,'file':f})
            self.sql('select hsrr.staging_to_readings();')
            return True
            
        except Exception as e:
            self.con.rollback()
            self.sql('delete from hsrr.staging;')
            return e


    def run_exists(self,run):
        r=self.sql('select count(run) as c from hsrr.run_info where run=%(run)s',{'run':run},ret=True)
        if r[0]['c']>0:
            return True

    #add charactors to ref until unique(ie run doesn't exist)
    def generate_run_name(self,ref):
        if not self.run_exists(ref):
            return ref
        
        r=ref
        i=0
        while self.run_exists(r):
            i+=1
            r='%s_%i'%(ref,i)
            
        return r
        
    def drop_runs(self,runs):
        runs="{"+','.join(runs)+"}"
        self.sql("delete from hsrr.run_info where run=any(%(runs)s::varchar[])",{'runs':runs})



    def process_run(self,run):
        self.run_cancelable_query(query='select hsrr.process(%(run)s)',args={'run':run},description='processing run '+run)
        #iface.messageBar().pushMessage('%s: processed run %s'%(self.prefix,run))


    def process_all(self):
        self.run_cancelable_query(query='select hsrr.process()',description='processing all runs')
        #iface.messageBar().pushMessage('%s: processed all runs'%(self.prefix))

        
    def get_runs(self):
        q=QSqlQuery(db=self.db)
        q.exec_('select run from hsrr.run_info order by run')
        runs=[]
        while q.next():
            runs.append(q.value(0))
        return runs


    def sects_to_routes_pk(self,sects):
        q = "select pk from hsrr.routes where sec=any('{%s}'::varchar[])"%(','.join(sects))
        return [r[0] for r in self.sql(q,ret=True)]


    def f_lines_to_routes_pk(self,f_lines):
        q = "select distinct pk from unnest('{%s}'::int[]) inner join hsrr.routes on s_line<=unnest and unnest<=e_line"%(','.join([str(f_line) for f_line in f_lines]))
        return [r[0] for r in self.sql(q,ret=True)]
    

#'sec':self.sec.text(),'rev':self.rev.isChecked(),'xsp':self.xsp.text(),'s':self.s_ch.value(),'e':self.e_ch.value(),'note':self.note.text(),'run':self.run_box.currentText()

   # def insert_into_routes(self,run,sec,rev,xsp,s_line,e_line,note,start_sec_ch,end_sec_ch):
        #self.sql('insert into hsrr.routes(run,sec,reversed,xsp,s_line,e_line,note,start_sec_ch,end_sec_ch values(%(run)s,%(sec)s,%(rev)s,%(xsp)s,%(s_line)s,%(e_line)s,%(note)s,%(start_sec_ch)s),%(end_sec_ch)s')


    #d is dict of column name and value
    def insert_into_routes(self,d):
        self.sql('insert into hsrr.routes(%s) values (%s)'%(','.join(d.keys()),','.join(['%('+k+')s' for k in d.keys()])),d)
        
   
#check row of hsrr spreadsheet
def is_valid(row):
    if len(row)>=15 and row[0]!='Position km':
        return row[0] and row[1] and row[2]  and row[12] and row[13] and row[14] and row[15]


#unused
#read line of hsrr spreadsheet. returns dict
def read_line(line,f_line,run):
    row=line.strip().split('\t')
    if is_valid(row):
        return {'raw_ch':float(row[0])*1000,'ts':row[1],'rl':row[2],'start_lon':row[12],'start_lat':row[13],'end_lon':row[14],'end_lat':row[15],'f_line':f_line,'run':run}


def parse_line(line,f_line,run):
    row=line.strip().split('\t')
    if is_valid(row):
        return ','.join([row[0],row[1],row[2],row[12],row[13],row[14],row[15],str(f_line),run])
    

def is_valid(row):
    if len(row)>=15 and row[0]!='Position km':
        return row[0] and row[1] and row[2]  and row[12] and row[13] and row[14] and row[15]
