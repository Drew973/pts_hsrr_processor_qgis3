from hsrr_processor.tests import test_network_model
from hsrr_processor.widgets import chainage_widget



if __name__ == '__console__':
    m = test_network_model.getModel()
    
    w = chainage_widget.chainageWidget()
    
    i = m.index(0,0)
    w.setIndex(i)

    w.show()

