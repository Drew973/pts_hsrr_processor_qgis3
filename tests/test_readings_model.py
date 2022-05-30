from hsrr_processor.widgets import add_row_dialog

from hsrr_processor.models import readings_model
from hsrr_processor.tests import get_db



def getModel(db = get_db.getDb()):
    return readings_model.readingsModel(db)


if __name__ == '__console__':
    m = getModel()
    m.setRun('A628 EB CL1')
  #  m.XYToFloat(0,0)#None. not near run.
    print(m.XYToFloat(419320.0,401456.9))#should be 14.66
    print(m.floatToXY(0))
    