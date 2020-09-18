from qgis.PyQt.QtGui import QBrush 
from qgis.PyQt.QtCore import Qt
from qgis.utils import iface

GAP_SIZE=1

#highlight where e_ch of row !=s_ch of next row or s_ch of row!=e_ch if last row

#i=index of model
def routes_color(i,disp=False):
    r=i.row()    
    m=i.model()
    
        
    e_ch_col=m.fieldIndex('e')#not same as self.e_ch col. Something to do with model vs view?
    
    #e_ch=m.index(r,e_ch_col).data()
    e_ch=i.sibling(0,e_ch_col).data()
    
    #last_e_ch=m.index(r-1,e_ch_col).data()#e_ch of last row
    last_e_ch=i.sibling(-1,e_ch_col).data()
        
    s_ch_col=m.fieldIndex('s')       
    #s_ch=m.index(r,s_ch_col).data()#start_ch of next row
    s_ch=i.sibling(0,e_ch_col).data()
    
   # next_s_ch=m.index(r+1,s_ch_col).data()#start_ch of next row
    next_s_ch=i.sibling(1,e_ch_col).data()    

          
    if disp:
        iface.messageBar().pushMessage(str(e_ch)+' '+str(next_s_ch))

                  
    if next_s_ch:# not None
        if e_ch>next_s_ch: #end_ch of row>s_ch of next row
            return QBrush(Qt.red)
                
        if next_s_ch-e_ch>GAP_SIZE:# gap between e_ch of row and s_ch of next row 
            return QBrush(Qt.yellow)
           

    if last_e_ch:#not none
        if last_e_ch>s_ch:#end_ch of last row>s_ch  
            return QBrush(Qt.red)
            
        if s_ch-last_e_ch>GAP_SIZE:   #gap between e_ch of last row and s_ch of row
            return QBrush(Qt.yellow)
        
        
def coverage_color(index):
    r=index.row()    
    m=index.model()

    if m.index(r,m.fieldIndex('hmds')).data() is None or m.index(r,m.fieldIndex('hmds')).data() =='':
        if m.index(r,m.fieldIndex('notes')).data() is None or m.index(r,m.fieldIndex('notes')).data() =='':
            return QBrush(Qt.red)
        else:
            return QBrush(Qt.yellow)
            
            
    
