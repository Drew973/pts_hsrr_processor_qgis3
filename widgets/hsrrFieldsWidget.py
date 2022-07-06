from hsrr_processor.widgets import fieldsWidget
#from hsrr_processor.functions import layer_functions
from qgis.core import QgsMapLayerProxyModel,QgsFieldProxyModel



class hsrrFieldsWidget(fieldsWidget.fieldsWidget):
    
    
    
    def __init__(self,parent=None):
                
        super(hsrrFieldsWidget,self).__init__(parent)
        
        self.addLayer('network','Layer with network','HSRR Processor:network layer not set',default='network')
        self.addField('label','Field with section label','HSRR Processor:section label field not set',default='sec',layer='network')
        
        self.addLayer('readings','Layer with readings','HSRR Processor:readings layer not set',default='readings')
        self.addField('run','Field with run','HSRR Processor:start chainage field not set',default='run',layer='readings')

        self.addField('s_ch','Field with start chainage of reading','HSRR Processor:start chainage field not set',default='s_ch',layer='readings')
        self.addField('e_ch','Field with end chainage of reading','HSRR Processor:end chainage field not set',default='e_ch',layer='readings')               
        
        self.getWidget('network').setFilters(QgsMapLayerProxyModel.LineLayer)
        self.getWidget('label').setFilters(QgsFieldProxyModel.String)    
        
        self.getWidget('readings').setFilters(QgsMapLayerProxyModel.LineLayer)
        self.getWidget('s_ch').setFilters(QgsFieldProxyModel.Numeric)    
        self.getWidget('e_ch').setFilters(QgsFieldProxyModel.Numeric)

        
    #def lowestSelectedReading(self,run):
      #  #returns 0 or lowest selectes reading        
    #    if self.isSet('readings') and self.isSet('s_ch') and self.isSet('run'):
   #         
     #       chainages= [f[self['s_ch']] for f in self['readings'].selectedFeatures() if f[self['run']]==run and f[self['s_ch']]]
     #       if chainages:
     #           return min(chainages) 
        
  #      return 0
            
    
    
 #   def selectOnNetwork(self,sects):
 #       layer = self['network']
 #       secField = self['label']
        
 #      if layer:
    #        layer_functions.selectByVals(sects, layer, secField)
 #   
    
    
   # def selectedSection(self):
     #   if self['label'] and self.getSelectedFeature('network'):
    #        return self.getSelectedFeature('network')[self['label']]



   # def filterReadingsLayer(self,run):
   #     layer = self['readings']
  #      field = self['run']
   #     layer.setSubsetString("%s = '%s'"%(field,run))
        