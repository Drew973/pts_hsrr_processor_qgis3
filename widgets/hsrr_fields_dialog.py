# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 08:37:22 2022

@author: Drew.Bennett

dialog to set layers and fields for models on accept.


"""


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog,QFormLayout,QHBoxLayout,QDialogButtonBox,QPushButton,QSizePolicy

from hsrr_processor.load_layers import load_network,load_readings

from hsrr_processor.widgets import field_box
from qgis.gui import QgsMapLayerComboBox

from qgis.core import QgsMapLayerProxyModel,QgsFieldProxyModel


'''
    deleting models could be problem. 
    running as Modal avoids this.
'''

class hsrrFieldsDialog(QDialog):
    
    
    
    
    def __init__(self,readingsModel,networkModel,parent=None):
        super().__init__(parent)
        self.readingsModel = readingsModel
        self.networkModel = networkModel
        
        self.setLayout(QFormLayout(self))
        
        
        self.network = QgsMapLayerComboBox(parent=self)
        self.network.setAllowEmptyLayer(True)
        self.network.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.network.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred)

       #attempt to set network to networkModel.layer() or 'network'
        if self.networkModel is not None:
            layer = self.networkModel.layer()
            if layer is None:
                layer = self.network.layer(self.network.findText('network'))
            self.network.setLayer(layer)
  
        
        loadNetworkButton = QPushButton('Import',parent=self)
        loadNetworkButton.clicked.connect(self.loadNetwork)
        loadNetworkButton.setToolTip('Import network into QGIS')
        self.addRow('Layer with network',[self.network,loadNetworkButton])


        self.sec = field_box.fieldBox(parent=self.network,default='sec')
        self.sec.setFilters(QgsFieldProxyModel.String)
        self.layout().addRow('Field with section label',self.sec)

        
        self.readings = QgsMapLayerComboBox(parent=self)
        self.readings.setFilters(QgsMapLayerProxyModel.LineLayer)
        self.readings.setAllowEmptyLayer(True)
        self.readings.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred)

       #attempt to set readings to readingsModel.layer() or 'network'
        if self.readingsModel is not None:
            layer = self.readingsModel.layer()
            if layer is None:
                layer = self.readings.layer(self.readings.findText('readings'))
            self.readings.setLayer(layer)
        
        loadReadingsButton = QPushButton('Import',parent=self)
        loadReadingsButton.setToolTip('Import readings into QGIS')
        loadReadingsButton.clicked.connect(self.loadReadings)
        
        self.addRow('Layer with readings',[self.readings,loadReadingsButton])



        self.run = field_box.fieldBox(parent=self.readings,default='run')
        self.run.setFilters(QgsFieldProxyModel.String)
        self.layout().addRow('Field with run',self.run)


        self.startChain = field_box.fieldBox(parent=self.readings,default='s_ch')
        self.startChain.setFilters(QgsFieldProxyModel.Numeric)
        self.layout().addRow('Field with start chainage',self.startChain)
        
        self.endChain = field_box.fieldBox(parent=self.readings,default='e_ch')
        self.endChain.setFilters(QgsFieldProxyModel.Numeric)
        self.layout().addRow('Field with end chainage',self.endChain)        
        
        
        
        # OK and Cancel buttons
        buttons = QDialogButtonBox(
        QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
        Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout().addWidget(buttons)
        
        
    #convenience method only used by init
    def addRow(self,label,widgets):
        layout = QHBoxLayout(self)
        for w in widgets:
            layout.addWidget(w)        
        self.layout().addRow(label,layout)
   
    
        
    def accept(self):
        if self.readingsModel is not None:
            self.readingsModel.setLayer(self.readings.currentLayer())
            self.readingsModel.setStartChainageField(self.startChain.currentField())
            self.readingsModel.setEndChainageField(self.endChain.currentField())
            self.readingsModel.setRunField(self.run.currentField())
            
        if self.networkModel is not None:
            self.networkModel.setLayer(self.network.currentLayer())
            self.networkModel.setField(self.sec.currentField())
        
        super().accept()



    def loadNetwork(self):
        self.network.setLayer(load_network.loadNetwork())
    
    
    
    def loadReadings(self):
        self.readings.setLayer(load_readings.loadReadings())
    
    

def hasMethod(ob,method):
    if hasattr(ob,method):
        f = ob.method
        if callable(f):
            return True
    return False
    

if __name__ == '__console__':
    d = hsrrFieldsDialog(None,None)
    d.exec_()
