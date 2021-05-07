from qgis.core import QgsTask

from qgis.utils import iface

from psycopg2.extras import execute_batch

from PyQt5.QtWidgets import QProgressDialog
import psycopg2




class cancelable_sql(QgsTask):



    def __init__(self,con,sql,args=None,sucess_message=None):
        QgsTask.__init__(self)
        self.con=con
        self.sql=sql
        self.args=args
        self.sucess_message=sucess_message
        



    def run(self):
      #  self.progress=QProgressDialog(parent=self.parent())#set parent to dockwidget
     #   self.progress.setWindowModality(Qt.WindowModal)#make modal to prevent multiple tasks at once
    #    self.progress.canceled.connect(self.cancel)
        
        cur=self.con.cursor()
        try:
            with self.con:
                if self.args:
                    cur.execute(self.sql,self.args)
                else:
                    cur.execute(self.sql)#with makes con commit here
            return True

        except Exception as e:
            self.err=e
            return False



#result bool

    def finished(self,result):
        iface.messageBar().clearWidgets()
        if result:
            if self.sucess_message:
                iface.messageBar().pushMessage(self.sucess_message)
        else:
            iface.messageBar().pushMessage(str(self.err))



    

    def cancel(self):
        self.con.cancel()#psycopg2 conection can be cancelled from any thread.
        QgsTask.cancel(self)


con = psycopg2.connect(host='localhost',database='hsrr_test',user='postgres',password='pts')
cur=con.cursor()
cur.execute("update hsrr.readings set ps_text=null",None)

#t = cancelable_sql(con,"update readings set ps_text=''",'done')
#t.run()

con.commit()
print('done')