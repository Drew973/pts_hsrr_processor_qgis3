# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialogButtonBox,QDialog,QFormLayout
import logging
logger = logging.getLogger(__name__)
from hsrr_processor.widgets import chainage_widget
from PyQt5.QtCore import QModelIndex



'''
dialog to add row to routesModel.
'''

class addRowDialog(QDialog):
    
    def __init__(self,parent=None):
        super().__init__(parent)
        
        self.setLayout(QFormLayout(self))
        
        self.runChWidget = chainage_widget.chainageWidget(parent=self)
        self.runChWidget.setToolTip('Run chainage.')
        self.layout().addRow('Run Chainage',self.runChWidget)
        
        self.setIndex(QModelIndex())        

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.layout().addWidget(self.buttons)

        self.buttons.rejected.connect(self.reject)
        self.buttons.accepted.connect(self.accept)
        
        
        
    def setIndex(self,index):
        logger.debug('setIndex(%s)',index)
        self.runChWidget.setIndex(index)


    def model(self):
        return self.runChWidget.getIndex().model()
        
       
    
    def accept(self):
        logger.debug('accept() model:%s',self.model())
        if self.model() is not None:
            self.model().addRow(startRunCh=self.runChWidget.value())
        super().accept()
