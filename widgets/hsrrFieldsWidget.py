from PyQt5.QtSql import QSqlDatabase
from qgis.gui import QgsFieldComboBox,QgsMapLayerComboBox
from qgis.PyQt.QtWidgets import QWidget,QFormLayout,QHBoxLayout,QPushButton
from qgis.utils import iface
from qgis.core import QgsProject
from hsrr_processor.widgets import layerFunctions
from qgis.core import QgsArrowSymbolLayer



class fieldComboBox(QgsFieldComboBox):
    #parent : QgsMapLayerComboBox
    #displayName  str
    def __init__(self,parent=None,layerBox=None,default='',displayName='',allowEmpty=True):
        super().__init__(parent)#bizare things happen when adding to menu with parent set 
        self.setAllowEmptyFieldName(allowEmpty)
        #self.setParent(parent)
        self.default = default
        if not layerBox is None:
            self.setLayer(layerBox.currentLayer())
            layerBox.layerChanged.connect(self.setLayer)
        
        
    def setLayer(self,layer):
        super().setLayer(layer)
        self.setField(self.default)
        

        
class layerComboBox(QgsMapLayerComboBox):
    
    def __init__(self,parent=None,displayName='',default='',allowEmpty=True):
        super().__init__(parent)
        self.fieldBoxes = []
        self.setAllowEmptyLayer(allowEmpty)
        
        L = QgsProject.instance().mapLayersByName(default)
        if L:
            self.setLayer(L[0])#qgis3        
        


class fieldsWidget(QWidget):
    
    def __init__(self,parent=None):
        super().__init__(parent)
        self.widgets = {}
        self.setLayout(QFormLayout())

        
    def add(self,widget,key,label):
        self.layout().addRow(label,widget)
        self.widgets.update({key:widget})
        
        
    def addRow(self,widget,key,label,others):
        row = QHBoxLayout()
        row.addWidget(widget)
        self.widgets.update({key:widget})
        for w in others:
            row.addWidget(w)
        self.layout().addRow(label,row)
        
        
    def widget(self,key):
        return self.widgets[key]
        
        
    def __getitem__(self,key):
        w = self.widgets[key]
        
        if isinstance(w,QgsMapLayerComboBox):#also true for subclasses
            return w.currentLayer()
        
        if isinstance(w,QgsFieldComboBox):
            return w.currentField()
        
    def isSet(self,key):
        return not self[key] is None
        
class hsrrFieldsWidget(fieldsWidget):
    
    def __init__(self,parent=None):
        super().__init__(parent)


        self.dockWidget = parent#parent is QStackedWidget?



        #network
        self.networkButton = QPushButton('Import',self)
        self.networkButton.setToolTip('Add new QGIS layer from database')
        self.networkButton.clicked.connect(self.importNetwork)

        self.addRow(layerComboBox(parent=self,default='network'),
        'network','Layer with network',[self.networkButton])
        
        self.add(fieldComboBox(self,self.widget('network'),'sec'),'label','Field with label')
       
        #readings
        self.readingsButton = QPushButton('Import',self)
        self.readingsButton.setToolTip('Add new QGIS layer from database')
        self.readingsButton.clicked.connect(self.importReadings)

        self.addRow(layerComboBox(parent=self,default='readings'),
        'readings','Layer with readings',[self.readingsButton])
        
        self.add(fieldComboBox(self,self.widget('readings'),'run'),'run','Field with run')
        self.add(fieldComboBox(self,self.widget('readings'),'s_ch'),'s_ch','Field with start chainage')
        self.add(fieldComboBox(self,self.widget('readings'),'e_ch'),'e_ch','Field with end chainage')

        #section_changes
        self.changesButton = QPushButton('Import',self)
        self.changesButton.setToolTip('Add new QGIS layer from database')
        self.changesButton.clicked.connect(self.importChanges)
        
        self.addRow(layerComboBox(parent=self,default='section_changes'),
        'changes','Layer with section changes',[self.changesButton])
        
                
        
    def setButtonsEnabled(self,enabled):       
        self.readingsButton.setEnabled(enabled)
        self.networkButton.setEnabled(enabled)
        self.changesButton.setEnabled(enabled)

      
        
    def importNetwork(self):
        if isinstance(self.dockWidget.database(),QSqlDatabase):
            if self.dockWidget.database().isOpen():
                layer = layerFunctions.importTable(self.dockWidget.database(),table='network',schema='hsrr',geometryColumn='geom')
                QgsProject.instance().addMapLayer(layer)
                toArrows(layer,{'color':'blue','is_curved':'False'})
                self.widget('network').setLayer(layer)
            
       
         
    def importReadings(self):
        if isinstance(self.dockWidget.database(),QSqlDatabase):
            if self.dockWidget.database().isOpen():
                layer = layerFunctions.importTable(self.dockWidget.database(),table='readings',schema='hsrr',geometryColumn='vect')
                QgsProject.instance().addMapLayer(layer)
                toArrows(layer,{'color':'green','is_curved':'False'})
                self.widget('readings').setLayer(layer)


    def importChanges(self):
        if isinstance(self.dockWidget.database(),QSqlDatabase):
            if self.dockWidget.database().isOpen():
                layer = layerFunctions.importTable(self.dockWidget.database(),table='section_changes',schema='hsrr',geometryColumn='pt')
                QgsProject.instance().addMapLayer(layer)
                self.widget('changes').setLayer(layer)



    def selectOnNetwork(self,sects):
        layer = self['network']
        secField = self['label']

        if layer is None or secField is None:
            return False
        else:
            layerFunctions.selectByVals(sects, layer, secField)
            layerFunctions.zoomToSelected(layer)
            return True

#data like [[run,s_ch,e_ch]]
#select readings in run that overlap s_ch to e_ch
    def selectOnReadings(self,data):
        print(data)
        layer = self['readings']
        s_chField = self['s_ch']
        e_chField = self['e_ch']
        runField = self['run']

        if not (layer is None or s_chField is None or e_chField is None or runField is None):
            def rowFilter(d):
                if d[2] is None:
                    e = '("%s"={run} and "%s">={s_ch})'%(runField,s_chField)
                    return e.format(run="'%s'"%(d[0]),s_ch=d[1])
                e = '("%s"={run} and "%s"<={e_ch} and "%s">={s_ch})'%(runField,s_chField,e_chField)
                return e.format(run="'%s'"%(d[0]),s_ch=d[1],e_ch=d[2])
           
            ex = ' or '.join([rowFilter(d) for d in data])
            print(ex)
            layer.selectByExpression(ex)


    def filterReadingsLayer(self,run):
        layer = self['readings']
        field = self['run']
        if not (layer is None or field is None):
            layer.setSubsetString("%s = '%s'"%(field,run))


    def lowestSelectedReading(self,run):
        #returns 0 or lowest selectes reading
        if self.isSet('readings') and self.isSet('s_ch') and self.isSet('run'):
            
            chainages= [f[self['s_ch']] for f in self['readings'].selectedFeatures() if f[self['run']]==run and f[self['s_ch']]]
            if chainages:
                return min(chainages) 
        
        return 0
            
            
'''
change layer symbology to arrows
https://nocache.qgis.org/api/3.4/qgsarrowsymbollayer_8cpp_source.html
'''
def toArrows(layer,properties={'color':'blue','is_curved':'False'}):
    sl = QgsArrowSymbolLayer.create(properties)
    layer.renderer().symbol().changeSymbolLayer(0,sl)#symbol has 1+ symbol layers
    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())#refresh symbology



if __name__ =='__console__':
    a = hsrrFieldsWidget()
    from PyQt5.QtSql import QSqlDatabase
    QSqlDatabase.removeDatabase('hsrr_test')
    db = QSqlDatabase.addDatabase('QPSQL','hsrr_test')
    db.close()
    db.setHostName('localhost')
    db.setDatabaseName('test')
    db.setUserName('postgres')
    print(db.open())

    a.setDb(db)
    a.show()

    a.filterReadingsLayer('SEW NB CL1')
    a.lowestSelectedReading('SEW NB CL1')
    a.selectOnReadings([['SEW NB CL1', 3.66237820760721, 4.24409647812409], ['SEW NB CL1', 4.24409647812409, None]])
    