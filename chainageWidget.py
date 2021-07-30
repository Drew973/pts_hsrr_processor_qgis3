from PyQt5.QtCore import pyqtSignal,Qt
from PyQt5.QtWidgets import QAction


from qgis.core import QgsSpatialIndex,QgsGeometry,QgsProject
from qgis.utils import iface
from qgis.gui import QgsMapToolEmitPoint



class runChainageTool(QgsMapToolEmitPoint):
    chainageFound = pyqtSignal(float)
    
    def __init__(self,layer=None,field=None):
        self.canvas = iface.mapCanvas() 
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.setLayer(layer,field)
        
    def setLayer(self,layer,field):
        self.layer = layer
        if layer:
            self.index = QgsSpatialIndex(layer.getFeatures(),None,QgsSpatialIndex.FlagStoreFeatureGeometries )
        self.field = field
        
    def canvasPressEvent( self, e ):
        if self.layer and self.index:
            point = self.toLayerCoordinates(self.layer,self.canvas.mouseLastXY())
            fid = self.index.nearestNeighbor(point)
            feat = self.layer.getFeature(fid[0])
            point = QgsGeometry.fromPointXY(point)
            #s_ch+0.1*st_LineLocatePoint
            self.chainageFound.emit(feat[self.field]+feat.geometry().lineLocatePoint(point)*0.1/feat.geometry().length())


#recursion error when try to do as method
def activate(tool):
    iface.mapCanvas().setMapTool(tool)

def deActivate(tool):
    iface.mapCanvas().unsetMapTool(tool)

from PyQt5.QtWidgets import QDoubleSpinBox,QMenu

class runChainageWidget(QDoubleSpinBox):
    
    #field=field with s_ch
    #layer=readings layer
    def __init__(self,parent=None,layer=None,field=None):
        super(runChainageWidget,self).__init__(parent)
        self.tool = runChainageTool(layer,None)
        self.tool.setLayer(layer,field)
        self.setSuffix('km')
        self.setSingleStep(0.1)#100m steps
        self.setDecimals(3)#3 decimal places =1m
        self.initContextMenu()
        self.tool.chainageFound.connect(self.setValue)
        self.tool.chainageFound.connect(lambda val:print(val))


   # getFeatures does not get filtered out features.
   #want nearest displayed feature
    def select(self):
        pass

        
    def initContextMenu(self):
        self.menu = QMenu(self)
        self.menu.setToolTipsVisible(True)
        
        self.fromClickAct = QAction('Set from click',self)
        self.fromClickAct.triggered.connect(lambda:activate(self.tool))
        self.menu.addAction(self.fromClickAct)

        self.selectAct = QAction('select on layer',self)
        self.selectAct.triggered.connect(self.select)
        self.menu.addAction(self.selectAct)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda pt:self.menu.exec_(self.mapToGlobal(pt)))
        
        
if __name__=='__console__':
    readingsLayer = QgsProject.instance().mapLayersByName('readings')[0]
    tool = runChainageWidget(layer=readingsLayer,field='s_ch')
    tool.show()

