from qgis.utils import iface
#from qgis.core import QgsRectangle#  QgsFeatureRequest

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
      

    
def selectOnNetwork(layer,labelField,sections):
    selectByVals(sections,layer,labelField)



'''
zoom canvas to extents of list of features(from any layer)

'''
def zoomToFeatures(features,scale=1.1,canvas=iface.mapCanvas()):

    e = None

    for f in features:
        if f.hasGeometry():
            if e is None:
                e = f.geometry().boundingBox()
            else:
                e.combineExtentWith(f.geometry().boundingBox())
                
    if e is not None:
        e.scale(scale)
        iface.mapCanvas().setExtent(e)
        iface.mapCanvas().refresh()
