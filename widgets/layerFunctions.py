from qgis.utils import iface
from qgis.core import QgsDataSourceUri,QgsVectorLayer,QgsProject
from qgis.core import QgsArrowSymbolLayer

import logging
logger = logging.getLogger(__name__)

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
    e = "%s IN (%s)" %(dq(field),','.join([sq(s) for s in vals]))#expression looks like "Column_Name" IN ('Value_1', 'Value_2', 'Value_N')
    logger.info(e)
    layer.selectByExpression(e)
        
        
#zoom to selected features of layer. Works with any crs
def zoomToSelected(layer):
    a = iface.activeLayer()
    iface.setActiveLayer(layer)
    iface.actionZoomToSelected().trigger()
    iface.setActiveLayer(a)
      


            
'''
change layer symbology to arrows
https://nocache.qgis.org/api/3.4/qgsarrowsymbollayer_8cpp_source.html
'''
def toArrows(layer,properties={'color':'blue','is_curved':'False'}):
    sl = QgsArrowSymbolLayer.create(properties)
    layer.renderer().symbol().changeSymbolLayer(0,sl)#symbol has 1+ symbol layers
    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())#refresh symbology

    
    

def importTable(db,table,schema='public',geometryColumn='geom',keyColumn='pk',layerName=None):
    
    if not layerName:
        layerName = table
    
    if db.port()==-1:
        port=None
    else:
        port = str(db.port())
        
    uri = QgsDataSourceUri()
    uri.setConnection(db.hostName(),port, db.databaseName() ,db.userName(),db.password())
    uri.setDataSource(schema, table, geometryColumn, aKeyColumn=keyColumn)
    layer = QgsVectorLayer(uri.uri(False), layerName, "postgres")
    QgsProject.instance().addMapLayer(layer)
    return layer
