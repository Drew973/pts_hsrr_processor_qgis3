# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialogButtonBox,QDialog,QFormLayout
from hsrr_processor.widgets import chainage_widget



class addRowDialog(QDialog):
    
    
    def __init__(self,parent=None):
        super().__init__(parent)
        
        self.setLayout(QFormLayout(self))
        
        self.runChWidget = chainage_widget.chainageWidget(parent=self)
        self.runChWidget.setToolTip('Run chainage.')
        self.layout().addRow('Run Chainage',self.runChWidget)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.rejected.connect(self.reject)
        self.buttons.accepted.connect(self.accept)
        
        self.layout().addWidget(self.buttons)
        
        self.setReadingsModel(None)
        self.setRouteModel(None)



#refresh min and max of spinbox and set chainage to lowest selected.
    def refresh(self):
        m = self.getReadingsModel()
        if m is not None:
            v = m.minSelected()
            if v is not None:
                self.runChWidget.setValue(v)
    
    
        self.runChWidget.setIndex(self.runChWidget.getIndex())



    def setReadingsModel(self,model):
        if model is not None:
           self.runChWidget.setIndex(model.index(0,0))



    def getReadingsModel(self):
        return self.runChWidget.getIndex().model()
        
       
        
    def setRouteModel(self,model):
        self.model = model
       
    
    
    def accept(self):
        if self.model is not None:
            self.model.insertRow(ch=self.runChWidget.value())
        super().accept()
