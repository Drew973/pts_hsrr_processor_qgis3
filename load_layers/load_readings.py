from hsrr_processor import load_layers
from qgis.core import QgsDataSourceUri
from qgis.utils import iface
from hsrr_processor.database import connection


def loadReadings(db=connection.getConnection()):
    uri = QgsDataSourceUri()
    uri.setConnection(db.hostName(), '5432', db.databaseName(), db.userName(), db.password())
    uri.setDataSource("hsrr", "readings", "vect",'','pk')
    layer = iface.addVectorLayer(uri.uri(False), 'readings','postgres')
    layer.loadNamedStyle(load_layers.readingsStyle)
    return layer


if __name__=='__console__':
    from hsrr_processor.tests import get_db
    db = get_db.getDb()
    loadReadings(db)
