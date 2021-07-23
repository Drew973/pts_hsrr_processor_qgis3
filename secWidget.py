from PyQt5.QtWidgets import QLineEdit,QAction


'''
class to select section

only allows valid section from model

select from network
select on network
'''


class secWidget(QLineEdit):

    

#fw = something with selectedSection() method
    def __init__(self ,fw,parent=None):
        super(secWidget,self).__init__(parent)
        self.fromLayerAct = QAction('Set from layer',self)
        self.fromLayerAct.triggered.connect(self.fromLayer)

        self.selectAct = QAction('select on layer',self)
        self.selectAct.triggered.connect(self.select)

        self.fw = fw
        
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
        self.fw.selectOnNetwork(self.text())
    
class standin:

    def __init__(self):
        pass
    
    def selectedSection(self):
        return '1300A1M/608'
    
    def selectOnNetwork(self):
        pass
    
if __name__=='__console__':
    
    s = standin()
    
    d = secWidget(s)
    d.show()
    