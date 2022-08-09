from PyQt5.QtCore import pyqtSignal

from qgis.core import QgsFeature
from qgis.gui import QgsMapToolEmitPoint



class nearestFeatureTool(QgsMapToolEmitPoint):
    featureFound = pyqtSignal(QgsFeature)
    
    def __init__(self,layer=None,index=None):
        self.canvas = iface.mapCanvas() 
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.layer = layer
        self.index = index
        
        
    def canvasPressEvent( self, e ):
        if self.layer and self.index:
            point = self.toLayerCoordinates(self.layer,self.canvas.mouseLastXY())
            fid = self.index.nearestNeighbor(point)
            feat = self.layer.getFeature(fid[0])
            self.featureFound.emit(feat)




if __name__=='__console__':
    readingsLayer = QgsProject.instance ().mapLayersByName('readings')[0]
    spIndex = QgsSpatialIndex(readingsLayer.getFeatures(),None,QgsSpatialIndex.FlagStoreFeatureGeometries )

    tool = nearestFeatureTool(layer=readingsLayer,index=spIndex)
    tool.featureFound.connect(lambda feat:print(feat['s_ch']))

    iface.mapCanvas().setMapTool(tool)

#iface.mapCanvas().unsetMapTool(tool)