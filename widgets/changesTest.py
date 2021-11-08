

from PyQt5.QtWidgets import QWidget,QUndoStack

import sys # added!
sys.path.append("..") # added!


import changesView



w = QWidget()


u = QUndoStack()

v = changesView.changesView()
w.layout().addWidget(v)



w.show()