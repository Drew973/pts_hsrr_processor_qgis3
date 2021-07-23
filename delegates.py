
from PyQt5.QtWidgets import QStyledItemDelegate,QLineEdit
from PyQt5.QtSql import QSqlRelationalDelegate
from PyQt5.QtWidgets import QComboBox,QLineEdit,QCompleter


#read only delegate ro display label
class readOnlyText(QStyledItemDelegate):
    
    def createEditor(self,parent,option,index):
        edit = QLineEdit(parent)
        edit.setReadOnly(True)
        return edit




class searchableRelationalDelegate(QSqlRelationalDelegate):
    
    
    def createEditor(self,parent,option,index):
        box = super(searchableRelationalDelegate,self).createEditor(parent,option,index)
        makeSearchable(box)
        return box




class lineEditRelationalDelegate(QSqlRelationalDelegate):
    
    
    def createEditor(self,parent,option,index):
        box = super(lineEditRelationalDelegate,self).createEditor(parent,option,index)
               
        edit = QLineEdit(parent)

        c = QCompleter(edit)
        c.setModel(box.model())
        c.setCompletionColumn(box.modelColumn())
        
        edit.setCompleter(c)
        return edit





# makes qComboBox b searchable
def makeSearchable(b):
    b.setEditable(True)
    b.setInsertPolicy(QComboBox.NoInsert)
    b.lineEdit().editingFinished.connect(lambda:b.setCurrentText(b.itemText(b.currentIndex())))
    
   # b.lineEdit().setCompleter()
    #editing finished triggered when lineEdit loses focus.
    #b.Model()
    #modelColumn()
    
    
   # QCompleter.setModel()
    #QCompleter.setCompletionColumn#column of model to use
    
    
    
'''
class fileWidgetDelegate : public QStyledItemDelegate
{
public:
    explicit fileWidgetDelegate(QObject *parent = nullptr,QString filter="");

    QWidget *createEditor(QWidget *parent, const QStyleOptionViewItem &option,const QModelIndex &index) const override;

    void setEditorData(QWidget *editor, const QModelIndex &index) const override;

    void setModelData(QWidget *editor, QAbstractItemModel *model,const QModelIndex &index) const override;


     // setTextEditable(false);
     // setFilter("Images (*.png *.bmp *.jpg)");


    void setTextEditable(bool editable);
    void setFilter(QString filt);

    bool textEditable=true;
    QString filter="";



};

#endif // FILEWIDGETDELEGATE_H







#include "filewidgetdelegate.h"
#include "filewidget.h"


fileWidgetDelegate::fileWidgetDelegate(QObject *parent,QString filter) : QStyledItemDelegate(parent)
{
    if (not filter.isEmpty()){setFilter(filter);}
}




QWidget *fileWidgetDelegate::createEditor(QWidget *parent,const QStyleOptionViewItem &option,const QModelIndex &index) const
{
     fileWidget * w = new fileWidget(parent);
     w->setTextEditable(textEditable);
     w->setFilter(filter);
     return w;
}


//see https://doc.qt.io/qt-5/qtwidgets-itemviews-spinboxdelegate-example.html
void fileWidgetDelegate::setEditorData(QWidget *editor, const QModelIndex &index) const
{
    fileWidget * fw = static_cast<fileWidget*>(editor);//editor to fileWidget *
    fw->setText(index.data().toString());
}


void fileWidgetDelegate::setModelData(QWidget *editor, QAbstractItemModel *model,const QModelIndex &index) const
{
    fileWidget * fw = static_cast<fileWidget*>(editor);//editor to fileWidget *
    model->setData(index, fw->currentFile(), Qt::EditRole);
}



void fileWidgetDelegate::setTextEditable(bool editable)
{
    textEditable=editable;
}



void fileWidgetDelegate::setFilter(QString filt)
{
    filter=filt;
}



'''