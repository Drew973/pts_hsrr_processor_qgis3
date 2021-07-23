
from qgis.gui import QgsFieldComboBox,QgsMapLayerComboBox
from qgis.PyQt.QtWidgets import QWidget,QFormLayout
from qgis.utils import iface






#set layer of qgsMapLayerComboBox to 1st layer named name if exists
def setLayerBoxTo(layerBox,layername):
    i = layerBox.findText(layername)
    if i != -1:
        layerBox.setLayer(layerBox.layer(i))
        
        
        
        
        
#default=thing to try to set to when layer changed

class field:
    def __init__(self,widget,message='',default=''):
        self.widget = widget
        self.message = message#message to display f field not set
        self.default = default


    def get(self):
        if self.widget.currentField():
            return self.widget.currentField()
        else:
            if self.message:
                iface.messageBar().pushMessage(self.message)   
                    
                
    def setLayer(self,layer):
        self.widget.setLayer(layer) 
        self.widget.setField(self.default)           


    def connectToLayerBox(self,layerBox):
        layerBox.layerChanged.connect(self.setLayer)
        self.setLayer(layerBox.currentLayer())


    def isSet(self):
        if self.widget.currentField():
            return True
        else:
            return False


#default=thing to try to set to when layer changed

class layer:
    def __init__(self,widget,message='',default=''):
        self.widget = widget
        self.message = message#message to display f field not set
        self.multipleFeaturesMessage=''
        self.noFeaturesMessage=''


    def get(self):
        if self.widget.currentLayer():
            return self.widget.currentLayer()
        else:
            if self.message:
                iface.messageBar().pushMessage(self.message)   


    def isSet(self):
        if self.widget.currentLayer():
            return True
        else:
            return False



    def getSelectedFeature(self):
        layer = self.get()
        
        if layer:
            
            r = None
            
            for f in layer.selectedFeatures():
                if r:
                    #already have feature
                    iface.messageBar().pushMessage(self.multipleFeaturesMessage)
                    return None
                
                if not r:
                    r=f
            #no features        
            if not r:
                iface.messageBar().pushMessage(self.noFeaturesMessage)
                return None
            
            return r






#collection of fields and layers
#creates own widgets.

class fieldsWidget(QWidget):
    
    def __init__(self,parent=None):
        super(fieldsWidget,self).__init__(parent)
        
        
        self.widgets = {}
        self.setLayout(QFormLayout())
        
    
        #layer is key or none
    def addField(self,key,label='',message='',default='',layer=None):
        w = QgsFieldComboBox(self)
        self.widgets.update({key:field(w,message,default)})
        
        self.layout().addRow(label,w)
        if layer:
            self.connectFieldToLayer(key,layer)
    
    
    def addLayer(self,key,label='',message='',default=''):
        w = QgsMapLayerComboBox(self)
        setLayerBoxTo(w,default)
        self.widgets.update({key:layer(w,message,default)})
        self.layout().addRow(label,w)


    #field and layer are keys
    def connectFieldToLayer(self,field,layer):
        self.widgets[field].connectToLayerBox(self.widgets[layer].widget)
    
    
    def getWidget(self,key):
        return self.widgets[key].widget
    
    
    def getSelectedFeature(self,key):
        return self.widgets[key].selectedFeature()
    
    def getField(self,key):
        pass
    
    
    def __getitem__(self,key):
        return self.widgets[key].get()

    
    def isSet(self,key):
        return self.widgets[key].isSet()


#unit test for qgis python console
if __name__ =='__console__':
    fw = fieldsWidget()
    fw.addLayer('network','Layer with network','HSRR Processor:network layer not set',default='network')
    fw.addField('label','Field with section label','HSRR Processor:section label field not set',default='sec',layer='network')
    
    fw.addLayer('readings','Layer with readings','HSRR Processor:readings layer not set',default='readings')
    fw.addField('s_ch','Field with start chainage of reading','HSRR Processor:start chainage field not set',default='s_ch',layer='readings')
    fw.addField('e_ch','Field with end chainage of reading','HSRR Processor:end chainage field not set',default='e_ch',layer='readings')

    fw.show()



    



    




    