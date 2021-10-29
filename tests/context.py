import os
import sys

print('file:',__file__)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


print('p:',os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import commands
from models import runInfoModel