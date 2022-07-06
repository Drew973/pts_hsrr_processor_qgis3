from hsrr_processor.models import run_info_model
from hsrr_processor.tests import get_db



def getModel(db = get_db.getDb()):
    return run_info_model.runInfoModel(db)


def testGenerateRunName(m):
    f = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\hsrr_processor\tests\example_data\A1M NB RE.xls'
    r = m.generateRunName(f)
    assert m.generateRunName('a') == 'a'
    print(r)


def testAddRun(m):
    run ='b'
    print(m.addRun(run))

m = getModel()
testGenerateRunName(m)
testAddRun(m)