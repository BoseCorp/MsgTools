import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *

from MsgApp import *

class MsgGui(MsgApp, QMainWindow):
    def __init__(self, name, argv, options, parent=None):
        # default to Network, unless we have a input filename that contains .txt
        headerName = "NetworkHeader"
        if any(".txt" in s for s in argv) or any(".TXT" in s for s in argv):
            headerName = "SerialHeader"

        QMainWindow.__init__(self,parent)
        MsgApp.__init__(self, name, headerName, argv, options)

        label = QLabel("<font size=40></font>")
        self.setCentralWidget(label)
         
        self.resize(320, 240)
        self.setWindowTitle(self.name)

        import Messaging
