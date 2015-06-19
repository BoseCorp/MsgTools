import sys
import uuid

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtNetwork import *

from TcpClientConnection import *

class MessageServer(QObject):
    connectionfailure = Signal()
    newconnectionaccepted = Signal()
    connectiondisconnected = Signal()

    def __init__(self, msgdir):
        super(MessageServer, self).__init__(None)

        self.msgdir = msgdir
        self.connections = {}
        self.tcpServer = QTcpServer()
        self.tcpServer.newConnection.connect(self.onNewConnection)

    def start(self):
        if not self.tcpServer.listen(QHostAddress.Any, 5678):
            self.connectionfailure.emit()
            return

    def onNewConnection(self):
        newConnection = TcpClientConnection(self.tcpServer.nextPendingConnection(), self.msgdir)

        newConnection.disconnected.connect(self.onConnectionDisconnected)
        newConnection.datareceived.connect(self.onDataReceived)
        newConnection.messagereceived.connect(self.onMessageReceived)

        self.connections[newConnection] = newConnection
        self.newconnectionaccepted.emit()

    def onConnectionDisconnected(self, connection):
        del self.connections[connection]
        self.connectiondisconnected.emit()

    def onDataReceived(self, data):
        # forward to all available client connections
        for connection in self.connections.values():
            connection.send(data)

    def onMessageReceived(self, message):
        pass
