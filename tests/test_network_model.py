

from hsrr_processor.widgets import add_row_dialog

from hsrr_processor.models import network_model
from hsrr_processor.tests import get_db



def getModel(db = get_db.getDb()):
    return network_model.networkModel(db)


if __name__ == '__console__':
    m = getModel()
  #  w = add_row_dialog.addRowDialog()
    
    
    
    