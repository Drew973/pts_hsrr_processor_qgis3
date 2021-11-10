from PyQt5.QtWidgets import QUndoCommand
import psycopg2

#from hsrr_processor.models import readingsModel,parseReadings

from hsrr_processor.models import readingsModel,parseReadings

def dbToCon(db):
    return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())


'''
    other commands should be added to stack after adding to section_changes...
    unless other user changes it.
    ensure nothing in section_changes before this?
    
'''
class uploadRunsCommand(QUndoCommand):

    def __init__(self,runInfoModel,uris,description='upload readings',parent=None):
        super().__init__(description,parent)
        self.runInfoModel = runInfoModel
        self.readingsModel = readingsModel.readingsModel(runInfoModel.database())
        self.uris = uris


    def redo(self):
        
        self.runs = {u:self.runInfoModel.addRun(u) for u in self.uris if parseReadings.isReadings(u)}#uri:run
        for k in self.runs:
            if k:
                self.readingsModel.uploadXls(k,self.runs[k])



    def undo(self):
        self.readingsModel.dropRuns(list(self.runs.values()))
        self.runInfoModel.dropRuns(list(self.runs.values()))

'''
    data in run_info,readings,section_changes
    delete from run_info no longer cascades
    reupload from file vs store readings?
    file location might change so better to store. memory usage?
    
'''
class dropRunsCommand(QUndoCommand):

    def __init__(self,runs,runInfoModel,sectionChangesModel,description='drop runs',parent=None):
        super().__init__(description,parent)
        self.runs = runs
        self.runInfoModel = runInfoModel
        self.sectionChangesModel = sectionChangesModel
        self.readingsModel = readingsModel.readingsModel(runInfoModel.database())
        

    def redo(self):
        
        self.readingsData = self.readingsModel.dropRuns(self.runs)
        self.changesData = self.sectionChangesModel.dropRuns(self.runs)
        self.runInfoData = self.runInfoModel.dropRuns(self.runs)

        
        
    def undo(self):
        self.runInfoModel.insertDicts(self.runInfoData)#needs to be 1st-foreign key
        self.readingsModel.uploadDicts(self.readingsData)
        self.sectionChangesModel.insertDicts(self.changesData)
        
        
        
        
 
        