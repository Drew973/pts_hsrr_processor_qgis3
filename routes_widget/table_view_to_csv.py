
try:
    from PyQt5.QtCore import Qt
except:
    from PyQt4.QtCore import Qt
    
#tv=table_view
#also does hidden columns of tv
def to_csv(tv,to,header=True):

    model=tv.model()
    col_range=range(0,model.columnCount())

    with open(to,'w') as to:

        if header:
            row=[]
            for c in col_range:
                row.append(str(model.headerData(c, Qt.Horizontal)))
            to.write(','.join(row)+'\n')
            
        for r in range(0,model.rowCount()):
            row=[]
            for c in col_range:
                #index = model.index(r,c)#QModelIndex
                row.append(str(model.index(r,c).data()))
            to.write(','.join(row)+'\n')
        


