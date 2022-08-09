
from hsrr_processor import load_layers
from hsrr_processor.database import connection

from qgis.core import QgsDataSourceUri
from qgis.utils import iface


def loadNetwork(db=connection.getConnection()):
    uri = QgsDataSourceUri()
    uri.setConnection(db.hostName(), '5432', db.databaseName(), db.userName(), db.password())
    uri.setDataSource("hsrr", "network", "geom",'','sec')
    layer = iface.addVectorLayer(uri.uri(False), 'network','postgres')
    layer.loadNamedStyle(load_layers.networkStyle)
    return layer


if __name__=='__console__':
    from hsrr_processor.tests import get_db

    db = get_db.getDb()
    loadNetwork(db)



