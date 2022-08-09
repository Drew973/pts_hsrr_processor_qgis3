
from hsrr_processor.tests import get_db
from hsrr_processor.database import connection

db1 = get_db.getDb()
print('db1:',db1.databaseName())

name = 'hsrrDatabase'
db2 = QSqlDatabase.database(connection.name)
print('db2:',db2.databaseName())

db2.isOpen()