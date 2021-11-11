# -*- coding: utf-8 -*-
"""
call test() from __init__ of dockwidget
"""

import logging
import os

from PyQt5.QtSql import QSqlDatabase

from hsrr_processor import hsrr_processor_dockwidget

#logging.basicConfig(filename = os.path.join(os.path.dirname(d),'hsrr_processor.log'),
#                    level=logging.INFO,filemode='w')


import unittest



def getDb():
    QSqlDatabase.removeDatabase('test')
    db = QSqlDatabase.addDatabase('QPSQL','test')
    db.close()
    db.setHostName('localhost')
    db.setDatabaseName('test')
    db.setUserName('postgres')
    assert db.open(),'could not open database'
    return db






'''
run unit tests and print results to 'tests/test_results.txt'
'''
def test(dockWidget):
    
    
    d = os.path.dirname(__file__)

    #unit tests    
    suite = unittest.defaultTestLoader.discover(start_dir=d,top_level_dir=d)
    
    with open(os.path.join(d,'test_results.txt'),'w') as f:
        runner = unittest.TextTestRunner(stream=f,verbosity=3)
        runner.run(suite)

    #dockWidget.show()#can easily display dockwidget

    #integration tests


    