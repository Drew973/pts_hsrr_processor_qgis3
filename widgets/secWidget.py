from PyQt5.QtWidgets import QLineEdit,QAction,QCompleter


'''
class to select section

only allows valid section from model

select from network
select on network
'''


class secWidget(QLineEdit):

    

#fw = something with selectedSection() method
    def __init__(self ,fw,parent=None,model=None,column=None):
        super(secWidget,self).__init__(parent)
        self.fromLayerAct = QAction('Set from layer',self)
        self.fromLayerAct.triggered.connect(self.fromLayer)

        self.selectAct = QAction('select on layer',self)
        self.selectAct.triggered.connect(self.select)

        self.fw = fw
        self.completer = QCompleter(self)
        self.setCompleter(self.completer)
        
        if model:
            self.setModel(model)
            
        if column:
            self.setColumn(column)
           
            
    def contextMenuEvent(self,event):
        menu = self.createStandardContextMenu()
        menu.addAction(self.selectAct)
        menu.addAction(self.fromLayerAct)
        menu.exec(event.globalPos())
    
    
    def fromLayer(self): 
        s = self.fw.selectedSection()
        if s:
            self.setText(s)
    
    
    def select(self):
        self.fw.selectOnNetwork([self.text()])
    
    
    def setModel(self,model):
        self.completer.setModel(model)
    
    
    def setColumn(self,col):
        self.completer.setCompletionColumn(col)
        
    
class standin:

    def __init__(self):
        pass
    
    def selectedSection(self):
        return '1300A1M/608'
    
    def selectOnNetwork(self,sec):
        pass
    
if __name__=='__console__':
    s = standin()
    d = secWidget(s)
    d.show()
    