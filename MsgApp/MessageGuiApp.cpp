#include <QTcpSocket>

#include "./MessageGuiApp.h"

MessageGuiApp::MessageGuiApp(MessageTranslator* msgTranslator)
 : QMainWindow(),
   _msgClient(new MessageClient(new QTcpSocket())),
   _msgTranslator(msgTranslator)
{
    connect(_msgClient, SIGNAL(newMessageComplete(Message*)), this, SIGNAL(newMessageReceived(Message*)));
}
