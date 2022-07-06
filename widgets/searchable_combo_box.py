
from PyQt5.QtWidgets import QComboBox#,QCompleter


#validator is for editing items etc.
class searchableComboBox(QComboBox):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
       # self.setCompleter(QCompleter(self.model(),self))
      #  self.completer().setCompletionMode(QCompleter.PopupCompletion)

         
    #set edit text to current item text when focused out.
    def focusOutEvent(self,e):
        
       # i = self.findText(self.currentText())#returns 0 text shouldn't be found.
        i = self.findData(self.currentText())

       
        if i!=-1:
            self.setCurrentIndex(i)
        
        else:
            self.setEditText(self.currentValue())
            
        super().focusOutEvent(e)
        
    
    
    def currentValue(self):
        return self.itemText(self.currentIndex())
    
    
if __name__=='__console__':
    w = searchableComboBox()
    w.insertItems(0,['1','2','3','40','50'])
    w.show()
    