
from hsrr_processor.tests import get_db
from hsrr_processor.database import setup

import logging
from hsrr_processor import init_logging
logger = logging.getLogger(__name__)

db = get_db.getDb()


def testSetupUi():
    msgBox = QMessageBox();
    msgBox.setInformativeText("Perform first time setup for database?");
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No);
    msgBox.setDefaultButton(QMessageBox.No);
    i = msgBox.exec_()
            
    if i==QMessageBox.Yes:
            
        r = setup.setupDb(db)
        print(r)
        logger.debug('setup result:%s',r)
            
        if r==True:
            iface.messageBar().pushMessage('fitting tool: prepared database')
        else:
            iface.messageBar().pushMessage('fitting tool:error preparing database:'+str(r))

#print(setup.setupDb(db))
testSetupUi()