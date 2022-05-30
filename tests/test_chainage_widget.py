
from hsrr_processor.tests import test_changes_model
from hsrr_processor.widgets import chainage_widget



if __name__ == '__console__':
    m = test_changes_model.createChangesModel()
    m.setRun('A57 EB LE')
    
    w = chainage_widget.chainageWidget()
    w.setIndex(m.index(1,m.fieldIndex('ch')))

    w.show()





