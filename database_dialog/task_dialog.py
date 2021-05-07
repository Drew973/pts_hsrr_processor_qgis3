import time
from PyQt5.QtWidgets import QDialog,QHBoxLayout,QLabel,QPushButton,QProgressBar

parent = None


import psycopg2


from qgis.core import (Qgis, QgsApplication, QgsMessageLog, QgsTask)


class taskDialog(QDialog):
    
    def __init__(self,parent=None):
        super().__init__(parent)
        
        self.setModal(True)
        
        self.setLayout(QHBoxLayout())
        
        self.label = QLabel(parent=self)
        self.layout().addWidget(self.label)
        
        self.cancelButton = QPushButton('Cancel',parent=self)
        self.layout().addWidget(self.cancelButton)
        
        #self.cancel_button.clicked.connect(self.task.cancel)
        self.progressBar = QProgressBar(self)
        self.layout().addWidget(self.progressBar)


#run a task. cancel button cancels task. 
#if noProgress is true progressBar will show busy but not move.

    def runTask(self,task,label,noProgress=True):
        self.label.setText(label)
        
        if noProgress:
            self.progressBar.setRange(0,0)
        else:
            self.progressBar.setRange(0,100)
            task.progressChanged.connect(self.progressBar.setProgress)

        self.cancelButton.clicked.connect(task.cancel)
        task.taskCompleted.connect(self.accept)
        task.taskTerminated.connect(self.reject)
        #task.run()#doesn't emit taskCompleted
        globals()['task1'] = task
        QgsApplication.taskManager().addTask(globals()['task1'] )

#con_params={'user': 'postgres', 'dbname': 'hsrr_test', 'host': 'localhost', 'port': '5432', 'tty': '', 'options': '', 'sslmode': 'prefer', 'sslcompression': '1', 'krbsrvname': 'postgres', 'target_session_attrs': 'any'}
#query='update hsrr.readings set ps_text=null'
#t = sqlTask(description='process run', connection_params=con_params,query=query)

#QgsApplication.taskManager().addTask(t1)

#pb = taskDialog(parent)
#pb.runTask(t,'running query')
#pb.show()
#time.sleep(10)
