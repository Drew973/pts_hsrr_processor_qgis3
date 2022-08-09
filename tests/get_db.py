# -*- coding: utf-8 -*-
"""
Created on Mon May 16 12:36:11 2022

@author: Drew.Bennett

create database from 'hsrr_test_db.json'. in plugins folder.
this file not included in git repo for security.


"""


from PyQt5.QtSql import QSqlDatabase
import json
import os
import hsrr_processor

from hsrr_processor.database import connection


def getDb():

    pluginFolder = os.path.dirname(os.path.dirname(hsrr_processor.__file__))
    configFile = os.path.join(pluginFolder,'hsrr_test_db.json')


    if not os.path.exists(configFile):
        raise KeyError('get_db missing config file {}'.format(configFile))
        

    with open(configFile,'r') as f:
        details = json.load(f)
    
        
    db = QSqlDatabase.addDatabase("QPSQL",connection.name)
    db.setHostName(details['host'])
    db.setDatabaseName(details['database'])
    db.setUserName(details['user'])
    db.setPassword(details['password'])


    if not db.open():
        raise ValueError('could not open database')

    return db
    
    
    