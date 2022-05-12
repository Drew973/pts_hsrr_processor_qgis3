from qgis.utils import iface
from qgis.core import QgsFeatureRequest

#layer=qgislayer
#section=string,

        
#single quote
def sq(s):
    return "'%s'"%(s)

#double quote
def dq(s):
    return '"%s"'%(s) 


#selects features of layer where field is in list vals
def selectByVals(vals,layer,field):
    e="%s IN (%s)" %(dq(field),','.join([sq(s) for s in vals]))#expression looks like "Column_Name" IN ('Value_1', 'Value_2', 'Value_N')
    layer.selectByExpression(e)
        
        
#zoom to selected features of layer. Works with any crs
def zoomToSelected(layer):
    a = iface.activeLayer()
    iface.setActiveLayer(layer)
    iface.actionZoomToSelected().trigger()
    iface.setActiveLayer(a)
      

'''
#returns fids in run and with s_chField-e_cFieldh overlapping s_ch and e_ch
#s_ch float
#e_ch float
def readingsFids(layer,run,runField,s_ch,s_chField,e_ch,e_chField):
    e = '{runField}={run} and {e_chField}>={s_ch} and {s_chField}<={e_ch}'
    e = e.format(runField=dq(runField),run=sq(run),e_chField=dq(e_chField),s_ch=s_ch,s_chField=dq(s_chField),e_ch=e_ch)
    request = QgsFeatureRequest().setFilterExpression(e) 
    return [f.id() for f in layer.getFeatures(request)]
    
    
#returns fids in run and with e_chField>ch
#s_ch float
#e_ch float
def readingsFids2(layer,run,runField,ch,e_chField):
    e = '{runField}={run} and {e_chField}>={ch}'
    e = e.format(runField=dq(runField),run=sq(run),e_chField=dq(e_chField),ch=ch)
    request = QgsFeatureRequest().setFilterExpression(e) 
    return [f.id() for f in layer.getFeatures(request)]


################################        
        
        
    

#filter layer to only show run
#run=string. run_field=fieldname with run
def filter_by_run(layer,run_field,run):
    layer.setSubsetString("%s = '%s'"%(run_field,run))
    
  '''  
    


