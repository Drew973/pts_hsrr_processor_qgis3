# -*- coding: utf-8 -*-


from PyQt5.QtSql import QSqlRelationalDelegate



from hsrr_processor.widgets import section_widget
    
'''

widget should try to switch to current Text on losing focus.
widget should be searchable.
   
   
   
widget destroyed as soon as focus lost?
/editing finished

   
'''
    
    

class secDelegate(QSqlRelationalDelegate):
    
    
    def __init__(self,parent,layer=None,labelField=None):
        super().__init__(parent)
        self.setLayer(layer)
        self.setLabelField(labelField)
        
        
    
    #index could be from any model.
    def createEditor(self,parent,option,index):
        a = super().createEditor(parent,option,index)
        
        b = section_widget.sectionWidget(parent)
        b.setModel(a.model())
        
        print(a.model())
        b.setLayer(self.getLayer())
        b.setLabelField(self.getLabelField())
      
        return b
    
    
    
    def setEditorData(self,editor,index):
        editor.setValue(index.data())
        
    
    #this happens on editor losing focus.
    
    def setModelData(self,editor, model, index):
        i = editor.findData(editor.currentText())
        
        print(editor.currentText(),i)
        
        
        if i!=-1:
            editor.setCurrentIndex(i)
        
        
        
        super().setModelData(editor,model,index)
    
    