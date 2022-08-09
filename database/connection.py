# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 15:05:29 2022

@author: Drew.Bennett
"""


from PyQt5.QtSql import QSqlDatabase



name = 'hsrrDatabase'
testName = 'hsrrTestConnection'



def getConnection():
    return QSqlDatabase.database(name)



def getTestConnection():
    return QSqlDatabase.database(testName)

