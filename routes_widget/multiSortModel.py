from PyQt5.QtCore import QSortFilterProxyModel


class multiColumnSortModel(QSortFilterProxyModel):


    #sortBy=[int] list of column indexes
    def setSortby(self,sortBy):
        self.sortBy=[sortBy]

#:sourceModel() to get column indexes? non unique names?


#returns bool. Left and Right are qmodelindex
    def  lessThan(self,Left,Right):
        row=Left.row()
        otherRow=Right.row()

        for i in self.sortBy:
            r=QSortFilterProxyModel.lessThan(self,Left.sibling(Left.row(),i),Right.sibling(Right.row(),i))
            if r:
                return r
            
        return r

    def sortColumn(self):
        return None



def sortedModel(model,sortBy):
    proxy=multiColumnSortModel()
    proxy.setSortBy(sortBy)
    proxy.setSourceModel(model)
    return proxy
