
from PyQt5.QtWidgets import QDialog,QLineEdit,QPlainTextEdit,QSpinBox,QComboBox,QApplication,QHBoxLayout,QVBoxLayout,QDoubleSpinBox,QCheckBox,QDialogButtonBox
import sys



def widgetVal(widget):
    
    if isinstance(widget,QLineEdit):
        return widget.text()
    
    if isinstance(widget,QPlainTextEdit):
        return widget.text()   

    if isinstance(widget,QSpinBox):
        return widget.value()
  
    if isinstance(widget,QDoubleSpinBox):
        return widget.value()   
  
    if isinstance(widget,QComboBox):
        return widget.currentText()

    if isinstance(widget,QCheckBox):
        return widget.isChecked()    
    
    

class dictDialog(QDialog):
    
    def __init__(self,widgets={},parent=None):
        self.widgets = widgets
        super(dictDialog, self).__init__(parent)
        #self.setLayout(QHBoxLayout())
        self.setLayout(QVBoxLayout())
        self.topLayout = QHBoxLayout()
        self.layout().addLayout(self.topLayout)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.rejected.connect(self.reject)
        self.buttons.accepted.connect(self.accept)
   
        self.layout().addWidget(self.buttons)
        
        
    def addWidget(self,name,widget,setTooltip=False):
        self.widgets.update({name:widget})
        self.topLayout.addWidget(widget)
        if setTooltip:
            widget.setToolTip(name)
        
        
    def getVals(self):
        return {k:widgetVal(self.widgets[k]) for k in self.widgets}
    
    
    def widget(self,key):
        return self.widgets[key]
    
    def __getitem__(self,key):
        return widgetVal(self.widgets[key])
    
    
    
    
if __name__ == "__main__":
    print('main')
    app = QApplication(sys.argv)
    d=dictDialog()
    d.addWidget('t',QLineEdit(),True)
    d.addWidget('num',QSpinBox(),True)
    d.addWidget('enum',QComboBox(),True)

    d.exec()
    

    sys.exit(app.exec())
    
    print(d.getVals())   

    