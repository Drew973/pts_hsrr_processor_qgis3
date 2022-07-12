# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 15:07:29 2022

@author: Drew.Bennett
"""

import logging

import os
logFile = os.path.join(os.path.dirname(__file__),'log.txt')                       
logging.basicConfig(filename=logFile,filemode='w',encoding='utf-8', level=logging.DEBUG, force=True)
