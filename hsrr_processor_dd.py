from .database_dialog.database_dialog import database_dialog

#import psycopg2
from psycopg2.extras import DictCursor,execute_batch
from os import path
from qgis.PyQt.QtSql import QSqlQuery



'''
subclass of database_dialog specific to scrim processor.

'''

class hsrr_dd(database_dialog):


#',' in note column is problem. fix with quote charactors?
    def upload_route(self,csv):
        with open(csv,'r') as f:
            self.cur.copy_expert('copy routes from STDIN with CSV HEADER',f)
            #c.copy_from(f,'routes',sep=',')
            self.con.commit()
            

    def download_routes(self,f):
        #self.query_to_csv(query='select * from routes order by run,s',to=s,force_quote='(run,sec,note)')
        self.cur.copy_expert("COPY routes TO STDOUT WITH (FORMAT CSV,HEADER,FORCE_QUOTE(run,sec,note),null '')",f)
        

    def setup_database(self):
        self.sql('create extension if not exists postgis;')
        self.sql('CREATE SCHEMA if not exists hsrr;')


        folder=path.join(path.dirname(__file__),'sql_scripts','setup_database')
        with open(path.join(folder,'setup.txt')) as f:
            for c in f.read().split(';'):
                com=c.strip()
                if com:
                    self.sql_script(path.join(folder,com))
      

    def autofit_run(self,run):
        self.sql('select hsrr.autofit_run(%(run)s)',{'run':run})

    
    def upload_run_csv(self,run):
        try:
            ref=path.splitext(path.basename(run))[0]

            self.sql('insert into hsrr.run_info(run,file) values(%(run)s,%(file)s);',{'run':ref,'file':run})


            with self.con:                
                q='''
with se as (select St_Transform(ST_SetSRID(ST_makePoint(%(start_lon)s,%(start_lat)s),4326),27700) as sp,ST_Transform(ST_SetSRID(ST_makePoint(%(end_lon)s,%(end_lat)s),4326),27700) as ep)
insert into hsrr.readings(run,raw_ch,t,f_line,rl,s_point,e_point,vect) 
(select %(run)s,%(raw_ch)s,to_timestamp(replace(%(ts)s,' ',''),'dd/mm/yyyyHH24:MI:ss'),%(f_line)s,%(rl)s,sp,ep,st_makeLine(sp,ep) from se)
        
                '''

                with open(run,'r',encoding='utf-8',errors='ignore') as f:
                    vals = [read_line(line,i+1,ref) for i,line in enumerate(f.readlines())]
                    vals = [v for v in vals if v]
                    execute_batch(self.cur,q,vals)
#            self.sql_script(path.join(path.dirname(__file__),'sql_scripts','update_run.sql'),{'run':ref})#run is name of run in run_info
            
            return True
            
        except Exception as e:
            self.con.rollback()
            return e


    def drop_runs(self,runs):
        runs="{"+','.join(runs)+"}"
        self.sql("delete from hsrr.run_info where run=any(%(runs)s::varchar[])",{'runs':runs})


    def refit_run(self,run):
        q='select hsrr.refit_run(%(run)s);select hsrr.resize_run(%(run)s);'
        self.cancelable_query(q=q,args={'run':run},text='refitting run:'+run,sucess_message='grip tester tool:refit run:'+run)


    def refit_runs(self,runs):        
        self.cancelable_queries(queries=['select hsrr.refit_all();','select hsrr.resize_all();'],args=None,text='refitting all runs',sucess_message='grip tester tool:refit runs')

        
    def get_runs(self):
        q=QSqlQuery(db=self.db)
        q.exec_('select run from hsrr.run_info order by run')
        runs=[]
        while q.next():
            runs.append(q.value(0))
        return runs


def is_valid(row):
    if len(row)>=15 and row[0]!='Position km':
        return row[0] and row[1] and row[2]  and row[12] and row[13] and row[14] and row[15]



#read line of readings .xls file
def read_line(line,f_line,run):
    row=line.strip().split('\t')
    if is_valid(row):
        return {'raw_ch':float(row[0])*1000,'ts':row[1],'rl':row[2],'start_lon':row[12],'start_lat':row[13],'end_lon':row[14],'end_lat':row[15],'f_line':f_line,'run':run}
    
