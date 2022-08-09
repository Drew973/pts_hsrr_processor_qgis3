from hsrr_processor.widgets import add_row_dialog

from hsrr_processor.models import readings_model
from hsrr_processor.tests import get_db



def getModel(db = get_db.getDb()):
    return readings_model.readingsModel(db)



def testXYToFloat(m):
    print(m.XYToFloat(419320.0,401456.9))#should be 14.66


def testFloatToXY(m):
    print(m.floatToXY(0))

#insert into hsrr.run_info values ('test_run','test file')
def test_loadSpreadsheet(m):
    testFolder = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\hsrr_processor\tests'
    file = os.path.join(testFolder,'example_data','M621 EB CL2.xls')
    m._loadSpreadsheet(fileName=file,run='test_run')



def test_dropRuns(m):
    runs = ['test_run']
    m._dropRuns(runs)



def testDropRuns(m):
    runs = ['test_run']
    m.dropRuns(runs)
    m.undo()

if __name__ == '__console__':
    m = getModel()
    m.setRun('A628 EB CL1')
    #test_dropRuns(m)
    test_loadSpreadsheet(m)
    testDropRuns(m)