# -*- coding: utf-8 -*-


from PyQt5.QtWidgets import QStyledItemDelegate



from hsrr_processor.widgets import section_widget
    
'''

widget should try to switch to current Text on losing focus.
widget should be searchable.
   
   
   
widget destroyed as soon as focus lost?
/editing finished

   
'''
    
    

class secDelegate(QStyledItemDelegate):
    
    
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setNetworkModel(None)
        
        
        
    def setNetworkModel(self,model):
        self._networkModel = model
        
        
        
    def getNetworkModel(self):
        return self._networkModel
    
        
    
    def createEditor(self,parent,option,index):
        w = section_widget.sectionWidget(parent)
        w.setModel(self.getNetworkModel())
        return w
    
    
    
    def setEditorData(self,editor,index):
        editor.setValue(index.data())
        
    
    
    #this happens on editor losing focus.
    def setModelData(self,editor, model, index):
        i = editor.findData(editor.currentText())
        if i!=-1:
            editor.setCurrentIndex(i)
        
        #"The default implementation gets the value to be stored in the data model from the editor widget's user property."
        super().setModelData(editor,model,index)
    
  