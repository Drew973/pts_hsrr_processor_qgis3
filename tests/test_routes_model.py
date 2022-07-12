from hsrr_processor.tests import get_db
from hsrr_processor.models import routes_model



db = get_db.getDb()
m = routes_model.routesModel(db)

i = m.index(0,0)
i = m.createIndex(0,0)
print(i.model())
m.setRun('M621 EB CL2')

m.addRow(startRunCh=0)


