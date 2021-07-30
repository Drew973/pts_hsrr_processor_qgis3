from .database_dialog import database_interface

import io
#import psycopg2
import os
import traceback


'''
subclass of database_interface specific to hsrr processor.

'''

class hsrr_dd(database_interface.database_interface):

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
       # self.run_setup_file(folder=f,file='setup.txt')
      
        con = self.get_con()
        with con:
            database_interface.runSetupFile(con=con,folder=f,file='setup.txt')
            
#move to model

    def process_run(self,run):
        self.run_cancelable_query(query='select hsrr.process(%(run)s)',args={'run':run},description='processing run '+run)
        #iface.messageBar().pushMessage('%s: processed run %s'%(self.prefix,run))

#move to model
    def process_all(self):
        self.run_cancelable_query(query='select hsrr.process()',description='processing all runs')
        #iface.messageBar().pushMessage('%s: processed all runs'%(self.prefix))



    def sects_to_routes_pk(self,sects):
        q = "select pk from hsrr.routes where sec=any('{%s}'::varchar[])"%(','.join(sects))
        return [r[0] for r in self.sql(q,ret=True)]


    def f_lines_to_routes_pk(self,f_lines):
        q = "select distinct pk from unnest('{%s}'::int[]) inner join hsrr.routes on s_line<=unnest and unnest<=e_line"%(','.join([str(f_line) for f_line in f_lines]))
        return [r[0] for r in self.sql(q,ret=True)]

 

        
    