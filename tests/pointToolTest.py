from qgis.gui import QgsMapToolEmitPoint

readingsLayer = QgsProject.instance ().mapLayersByName('readings')[0]
spIndex = QgsSpatialIndex(readingsLayer.getFeatures(),None,QgsSpatialIndex.FlagStoreFeatureGeometries )

#canvasClicked signal
class printClickedPoint(QgsMapToolEmitPoint):
    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)

    def canvasPressEvent( self, e ):
        #point = self.toMapCoordinates(self.canvas.mouseLastXY())
        point = self.toLayerCoordinates(readingsLayer,self.canvas.mouseLastXY())
        print(point)
        fid = spIndex.nearestNeighbor(point)
        feat = readingsLayer.getFeature(fid[0])
        print(feat['s_ch'])

canvas_clicked = printClickedPoint( iface.mapCanvas() )
iface.mapCanvas().setMapTool(canvas_clicked)

#iface.mapCanvas().unsetMapTool(canvas_clicked)

