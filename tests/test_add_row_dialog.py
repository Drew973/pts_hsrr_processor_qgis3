from qgis.core import QgsProject

from hsrr_processor.widgets import add_row_dialog
from hsrr_processor.tests import test_network_model,test_readings_model


def testWidget(model=test_network_model.getModel()):
    w = add_row_dialog.addRowDialog()
    w.setNetworkModel(model)
    w.show()
    return w


nm = test_network_model.getModel()
nm.setLayer(QgsProject.instance().mapLayersByName('network')[0])
nm.setField('sec')


rm = test_readings_model.getModel()
rm.setRun('A628 WB CL1')
rm.setLayer(QgsProject.instance().mapLayersByName('readings')[0])
rm.setStartChainageField('s_ch')

w = testWidget()
w.setNetworkModel(nm)
w.setReadingsModel(rm)



