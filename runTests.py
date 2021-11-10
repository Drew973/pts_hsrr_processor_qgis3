# -*- coding: utf-8 -*-
"""
call test() from __innit__ of dockwidget
"""

import logging
import os


d = os.path.dirname(__file__)

logging.basicConfig(filename = os.path.join(os.path.dirname(d),'hsrr_processor.log'),
                    level=logging.INFO,filemode='w')


import unittest


#from hsrr_processor.tests import test_run_info



'''
run unit tests and print results to 'tests/test_results.txt'
'''
def test(dockWidget):

    suite = unittest.defaultTestLoader.discover(start_dir=d,top_level_dir=d)
    
    with open(os.path.join(d,'tests','test_results.txt'),'w') as f:
        runner = unittest.TextTestRunner(stream=f,verbosity=3)
        result = runner.run(suite)
        print(result)

