

from hsrr_processor.widgets import add_row_dialog

from hsrr_processor.models import network_model
from hsrr_processor.tests import get_db
from hsrr_processor.database import connection


def getModel(db = get_db.getDb()):
    return network_model.networkModel()


def testSecLength(model):
    assert model.secLength(r'4700A1/338') == 0.35100000000000003
    assert model.secLength('invalid section') == 0.0


def testSecChToXY(model):
    print(model.secChToXY(sec=r'4700A1/338',ch=0))
    print(model.secChToXY(sec='invalid section',ch=0))


def testXYToSecCh(model):
    print(model.XYToSecCh(0,0,'invalid section'))
    print(model.XYToSecCh(0,0,r'4700A1/338'))


if __name__ == '__console__':
    m = getModel()
  #  w = add_row_dialog.addRowDialog()
    testSecLength(m)
    testSecChToXY(m)
    testXYToSecCh(m)
    