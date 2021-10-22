from PyQt5.QtWidgets import QUndoCommand
import psycopg2




def dbToCon(db):
    return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())


'''
    other commands should be added to stack after adding to section_changes...
    unless other user changes it.
    ensure nothing in section_changes before this?
    
'''
class uploadCommand(QUndoCommand):

    def __init__(self,model,readings,description='upload readings',parent=None):
        super().__init__(description,parent)
        self.model = model
        self.readings = readings


    def redo(self):
        self.run = self.model.uploadReadings(self.readings)


    def undo(self):
        if self.model.secChangesCount(self.run)==0:
            self.model.dropRuns([self.run])
        else:
            pass


'''
    data in run_info,readings,section_changes
    delete from run_info cascades
    reupload from file vs store readings?
    file location might change so better to store. memory usage?
    
'''
class dropRunCommand(QUndoCommand):

    def __init__(self,run,runInfoModel,sectionChangesModel,description='upload readings',parent=None):
        super().__init__(description,parent)
        self.run = run
        self.runInfoModel = runInfoModel
        self.sectionChangesModel = sectionChangesModel
        

    def redo(self):
        self.sectionChangesModel.dropRowsCommand(parent=self,pks=self.sectionChangesModel.pks(self.run))
        
        with dbToCon(self.sectionChangesModel.database()) as con:
            con.cursor().execute("delete from hsrr.readings where run = %(run)s returning run,f_line,t,raw_ch,rl,st_asText(vect),s_ch,e_ch",{'run':self.run})
        
        super().redo()
        
        
    #def undo(self):
        
