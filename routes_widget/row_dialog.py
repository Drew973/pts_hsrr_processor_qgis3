import os
from  qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog
from qgis.utils import iface
from qgis.PyQt.QtCore import QSettings
#from qgis.gui import QgsFieldProxyModel#qgis 2
from qgis.core import QgsFieldProxyModel#qgis 3

def fixHeaders(path):
    with open(path) as f:
        t=f.read()
    r={'qgsfieldcombobox.h':'qgis.gui','qgsmaplayercombobox.h':'qgis.gui'}
    for i in r:
        t=t.replace(i,r[i])
    with open(path, "w") as f:
        f.write(t)


uiPath=os.path.join(os.path.dirname(__file__), 'add_dialog.ui')
fixHeaders(uiPath)
FORM_CLASS, _ = uic.loadUiType(uiPath)


class row_dialog(QDialog,FORM_CLASS):
    
    def __init__(self,dd,model,network_box,sec_fieldbox,readings_box,run_fieldbox,f_line_fieldbox,run_box,vals=None,parent=None):
        super(QDialog,self).__init__(parent)
        self.setupUi(self)

        self.dd=dd
        
        self.cancel_button.clicked.connect(self.reject)
        self.sec_from_selected_button.clicked.connect(self.sec_from_selected)
        self.s_ch_from_selected_button.clicked.connect(self.s_ch_from_selected)
        self.e_ch_from_selected_button.clicked.connect(self.e_ch_from_selected)
        
        self.network_box=network_box
        self.sec_fieldbox=sec_fieldbox
        self.run_box=run_box

        self.model=model
        
        if vals:
            self.set_row(vals)
            self.ok_button.clicked.connect(self.edit)
            self.old_vals=self.get()
            
        else:
            self.ok_button.clicked.connect(self.add)


    #set edits from dict vals. 
    def set_row(self,vals):
        self.sec.setText(vals['sec'])
        self.xsp.setText(vals['xsp'])
        self.rev.setChecked(vals['rev'])

        self.s_ch.setValue(vals['s_ch'])
        self.e_ch.setValue(vals['e_ch'])
        self.note.setText(vals['note'])        
    
    
    def add(self):
        #self.insert(**self.get())
        self.insert()
        self.accept()

        

    def edit(self):
        if self.old_vals!=self.get():
            self.drop(**self.old_vals)
            self.insert(**self.get())
            self.route_model.select()
            self.accept()

    def get(self):
        return {'sec':self.sec.text(),'rev':self.rev.isChecked(),'xsp':self.xsp.text(),'s':self.s_ch.value(),'e':self.e_ch.value(),'note':self.note.text(),'run':self.run_box.currentText()}

        
    def insert(self):
        #self.dd.sql3("insert into routes(sec,xsp,run,reversed,s,e,note) values(%(sec)s,%(xsp)s,%(run)s,%(rev)s,%(s)s,%(e)s,%(note)s)",self.get())
       # self.dd.db.transaction()
        
        r=self.model.record()
        d=self.get()
        [r.setValue(k,d[k]) for k in d];


        r.remove(r.indexOf('pk'))#delete pk value. To let autoincrementing happen?
        #r.setGenerated(r.indexOf('pk'),True)#allows database to generate this
        #r.setValue(r.indexOf('pk'),None)
        
        if self.model.insertRecord(-1, r):
        #qDebug()<<"successful insertion";
            self.model.submitAll()
        #else:
            #self.model.revertAll()
        #    self.dd.db.rollback()

    
    def drop(self):
        self.dd.sql3("delete from routes where sec=%(sec)s and xsp=%(xsp)s and reversed=%(rev)s and run=%(run)s and s=%(s)d and e=%(e)d and note=%(note)s",self.get())

        

    def sec_from_selected(self):
        layer= self.network_box.currentLayer()
        al=iface.activeLayer()
        
        if al!=layer:
            iface.messageBar().pushMessage('fitting tool: layer is not network layer. check under layers tab')
            return
            
        sf=al.selectedFeatures()

        if len(sf)>1:
            iface.messageBar().pushMessage('fitting tool: more than 1 feature selected')
            return

        if sf==[]:
            iface.messageBar().pushMessage('fitting tool: no features selected')
            return
        
        self.sec.setText(sf[0][self.sec_fieldbox.currentField()])

        
    def s_ch_from_selected(self):
        layer= self.readings_box.currentLayer()
        
        if al!=layer:
            iface.messageBar().pushMessage('fitting tool: layer is not zm3 layer. check under layers tab')
            return
        
        chainages=[f[self.f_line_fieldbox.currentField()] for f in layer.selectedFeatures()]

        if not chainages:
            iface.messageBar().pushMessage('fitting tool: no features selected')
            return
        
        self.s_ch.setValue(min(chainages))

        
    def e_ch_from_selected(self):
        layer= self.readings_box.currentLayer()
        
        if al!=layer:
            iface.messageBar().pushMessage('fitting tool: layer is not zm3 layer. check under layers tab')
            return
        
        chainages=[f[self.f_line_fieldbox.currentField()] for f in layer.selectedFeatures()]

        if not chainages:
            iface.messageBar().pushMessage('fitting tool: no features selected')
            return
        
        self.e_ch.setValue(max(chainages))


        
#i=index of sqlTableModel.
#returns dict of that index's row
def row_to_dict(i):
    r=i.row()
    m=i.model()

    d={}
    for col in range(0,m.columnCount()):
        d.update({m.record().fieldName(col):i.sibling(r,col).data()})

    return d






                                               
