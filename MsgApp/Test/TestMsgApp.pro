#-------------------------------------------------
#
# Project created by QtCreator 2014-06-13T15:11:59
#
#-------------------------------------------------
include(../../mk/qtcommon.pri)

INCLUDEPATH += .

QT       += core testlib

TARGET = TestMsgApp
TEMPLATE = app

SOURCES += main.cpp\

HEADERS  += ../MessageClient.h \
    $$MSGDIR/Cpp/Network.h \
    ../Message.h \
    ../FieldInfo.h \
    ../MsgInfo.h \
    ../Reflection.h

INCLUDEPATH += $$BUILDROOT/ThirdParty/gmock-1.6.0/gtest/include $$OBJDIR

LIBS += -L$$BUILDROOT/ThirdParty/gmock-1.6.0/obj/ -lgtest
