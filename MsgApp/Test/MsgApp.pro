#-------------------------------------------------
#
# Project created by QtCreator 2014-06-13T15:11:59
#
#-------------------------------------------------

INCLUDEPATH += .

QT       += core

TARGET = MsgApp
TEMPLATE = app

SOURCES += main.cpp\

HEADERS  += ../MessageClient.h \
    ../../CodeGenerator/obj/Cpp/Network.h \
    ../Message.h

INCLUDEPATH += ../../CodeGenerator ../../ThirdParty/gmock-1.6.0/gtest/include


LIBS += -L../../ThirdParty/gmock-1.6.0/obj/ -lgtest
