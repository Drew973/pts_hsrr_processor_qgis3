from qgis.gui import QgsFieldComboBox,QgsMapLayerComboBox
from qgis.PyQt.QtWidgets import QWidget,QFormLayout,QMenu,QWidgetAction,QHBoxLayout,QLabel
from collections import OrderedDict
from qgis.core import QgsProject 


def toWidgetAction(widget,parent=None,desc=''):
    print(widget,parent,desc)
    a = QWidgetAction(parent)
    a.setDefaultWidget(widget)
    a.setText(desc)
    return a
    
    
class layerComboBox(QgsMapLayerComboBox):
    
    def __init__(self,parent=None,displayName='',default=''):
        super().__init__(parent)
        self.displayName = displayName
        self.fieldBoxes = []
        
        L = QgsProject.instance().mapLayersByName(default)
        if L:
            self.setLayer(L[0])#qgis3
        
        
    def addToMenu(self,menu):#not working yet
        #when widget has child child's fields are used!?
        print('add to menu')
        a = QWidgetAction(menu)
        
        w = QWidget(menu)
        w.setLayout(QHBoxLayout())
        w.layout().addWidget(QLabel(self.displayName))
        w.layout().addWidget(self)
       # a.setDefaultWidget(w)
    
        
      #  a.setDefaultWidget(self)
      #  a.setText(self.displayName)#does nothing
      #  menu.addAction(a)
        
    def addFieldBox(self,fb):
        self.fieldBoxes.append(fb)


class FieldComboBox(QgsFieldComboBox):
    #parent : QgsMapLayerComboBox
    #displayName  str
    def __init__(self,parent=None,layerBox=None,default='',displayName=''):
        super().__init__(parent)#bizare things happen when adding to menu with parent set 

        #self.setParent(parent)
        self.default = default
        self.displayName = displayName
        if not layerBox is None:
            self.setLayer(layerBox.currentLayer())
            layerBox.layerChanged.connect(self.setLayer)
            layerBox.addFieldBox(self)
        
        
    def setLayer(self,layer):
        super().setLayer(layer)
        self.setField(self.default)
        
 
    def addToMenu(self,menu):
        #when widget has child child's fields are used!?
        a = QWidgetAction(menu)
        a.setText(self.displayName)#does nothing
        
        w = QWidget(menu)
        w.setLayout(QHBoxLayout())
        w.layout().addWidget(QLabel(self.displayName))
        w.layout().addWidget(self)
        a.setDefaultWidget(w)
        
        menu.addAction(a)


class fieldMapper:
    def __init__(self):
        self.widgets = OrderedDict()
        
    def addLayer(self,key,widget):
        self.widgets[key] = widget
        
    def addField(self,key,widget):
        self.widgets[key] = widget
        
    def __getitem__(self,key):
        w = self.widgets[key]
        
        if isinstance(w,QgsMapLayerComboBox):#also true for subclasses
            return w.currentLayer()
        
        if isinstance(w,QgsFieldComboBox):
            return w.currentField()

    def widget(self,key):
        return self.widgets[key]
        
    #add to existing QFormLayout
    def addToFormLayout(self,layout):
        for k in self.widgets:
            layout.addRow(self.widgets[k].displayName,self.widgets[k])
        
    #add to existing QMenu
    #adds submenu per layer
    
    def addToMenu(self,menu):#not working yet
       # pass
        #menu.addAction(toWidgetAction(self.fieldBox,self))
        for w in self.widgets.values():
            if isinstance(w,layerComboBox):
                m = menu.addMenu(w.displayName)
                w.addToMenu(m)
                for fb in w.fieldBoxes:
                    fb.addToMenu(m)
        
        
if __name__ =='__console__':
    w = QWidget()
    m = fieldMapper()
    
    layerBox = layerComboBox(displayName='network layer',default='network')
    m.addLayer('networkLayer',layerBox)
    m.addField('sec',FieldComboBox(layerBox=m.widget('networkLayer'),displayName='label field',default='sec',parent=layerBox))
    layout = QFormLayout()
    m.addToFormLayout(layout)
  #  m.addToMenu(None)
    w.setLayout(layout)
    
    menu = QMenu(w)
    

    #m.addToMenu(menu)
    w.setContextMenuPolicy(Qt.CustomContextMenu)
    w.customContextMenuRequested.connect(lambda pt:menu.exec_(w.mapToGlobal(pt)))
    
    w.show()
    