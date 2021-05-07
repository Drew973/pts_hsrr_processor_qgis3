import psycopg2


from qgis.core import (Qgis, QgsApplication, QgsMessageLog, QgsTask)

MESSAGE_CATEGORY = 'My subclass tasks'


#QgsTask is buggy and badly documented.
#trying to use multithreading through other methods crashes QGIS.





#calling print or altering gui from seperate thread(ie in run method) will cause crashes.
class sqlTask(QgsTask):
    """This shows how to subclass QgsTask"""

#connection_params from con.get_dsn_parameters()
    def __init__(self,description,connection_params,query,args=None):

        super().__init__(description, QgsTask.CanCancel)
        self.total = 0
        self.iterations = 0
        self.exception = None
        self.connection_params=connection_params
        self.query=query
        self.args=args



#tasks started through run method don't seem to emit taskCompleted signal

    def run(self):
        """Here you implement your heavy lifting. This method should
        periodically test for isCancelled() to gracefully abort.
        This method MUST return True or False
        raising exceptions will crash QGIS so we handle them internally and
        raise them in self.finished
        """
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.description()), MESSAGE_CATEGORY, Qgis.Info)
        try:
                
            with psycopg2.connect(**self.connection_params) as con:
                cur=con.cursor()
                cur.execute(self.query,self.args)
                con.commit()
            return True
        
        except Exception as e:
            self.exception=e
            return False

    def finished(self, result):
        """This method is automatically called when self.run returns.
        result is the return value from self.run.
        This function is automatically called when the task has completed (
        successfully or otherwise). You just implement finished() to do 
        whatever
        follow up stuff should happen after the task is complete. finished is
        always called from the main thread, so it's safe to do GUI
        operations and raise Python exceptions here.
        """
        if result:
            QgsMessageLog.logMessage(
                'Task "{name}" completed\n Query: {query} \n args {args}'.format(
                name=self.description(),query=self.query,args=self.args),
                MESSAGE_CATEGORY, Qgis.Success)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage(
                    'Task "{name}" not successful but without exception ' \
                    '(probably the task was manually canceled by the '
                    'user)'.format(
                        name=self.description()),
                    MESSAGE_CATEGORY, Qgis.Warning)
            else:
                QgsMessageLog.logMessage(
                    'Task "{name}" Exception: {exception}'.format(
                        name=self.description(), exception=self.exception),
                    MESSAGE_CATEGORY, Qgis.Critical)
                raise self.exception

    def cancel(self):
        QgsMessageLog.logMessage(
            'Task "{name}" was cancelled'.format(name=self.description()),
            MESSAGE_CATEGORY, Qgis.Info)
        super().cancel()


#calling QgsApplication.taskManager().addTask from functions or method doesn't always start task. scope issue. fix using globals.

def startTask(task):
    globals()['task1'] = task
    QgsApplication.taskManager().addTask(globals()['task1'] )



#con_params={'user': 'postgres', 'dbname': 'hsrr_test', 'host': 'localhost', 'port': '5432', 'tty': '', 'options': '', 'sslmode': 'prefer', 'sslcompression': '1', 'krbsrvname': 'postgres', 'target_session_attrs': 'any'}
#query='update hsrr.readings set ps_text=null'
#t1 = sqlTask(description='waste cpu long', connection_params=con_params,query=query)

#QgsApplication.taskManager().addTask(t1)
