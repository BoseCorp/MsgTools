#    <OUTPUTFILENAME>
#    Created <DATE> from:
#        Messages = <INPUTFILENAME>
#        Template = <TEMPLATEFILENAME>
#        Language = <LANGUAGEFILENAME>
#
#                     AUTOGENERATED FILE, DO NOT EDIT
import struct
import ctypes
from collections import OrderedDict
from msgtools.lib.messaging import *
import msgtools.lib.messaging as msg

class <MSGNAME> :
    SIZE = <MSGSIZE>
    MSG_OFFSET = 0
    # Enumerations
    <ENUMERATIONS>

    #@staticmethod
    #def Create() :
    #    message_buffer = ctypes.create_string_buffer(<MSGNAME>.SIZE)
    #    <INIT_CODE>
    #    return message_buffer
    
    def __init__(self, messageBuffer=None):
        doInit = 0
        if messageBuffer == None:
            doInit = 1
            messageBuffer = ctypes.create_string_buffer(<MSGNAME>.SIZE)
        else:
            try:
                messageBuffer.raw
            except AttributeError:
                newbuf = ctypes.create_string_buffer(len(messageBuffer))
                for i in range(0, len(messageBuffer)):
                    newbuf[i] = bytes(messageBuffer)[i]
                messageBuffer = newbuf
        # this is a trick to get us to store a copy of a pointer to a buffer, rather than making a copy of the buffer
        self.msg_buffer_wrapper = { "msg_buffer": messageBuffer }
        if doInit:
            self.initialize()

    def initialize(self):
            <INIT_CODE>
            pass
    
    def rawBuffer(self):
        # this is a trick to get us to store a copy of a pointer to a buffer, rather than making a copy of the buffer
        return self.msg_buffer_wrapper["msg_buffer"]

    @staticmethod
    def MsgName():
        return "<MSGNAME>"

    def SetMessageID(self, id):
        <SETMSGID>

    def GetMessageID(self):
        id = <GETMSGID>
        return id

    def __repr__(self):
        def add_param(n, v):
            if v == '':
                v = '""'
            if ',' in v and not((v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'"))):
                v = '"%s"' % v
            return n + " = " + v + ", "
        ret = ''
        for fieldInfo in self.fields:
            if(fieldInfo.count == 1):
                if len(fieldInfo.bitfieldInfo) == 0:
                    ret += add_param(fieldInfo.name, str(Messaging.get(self, fieldInfo)))
                else:
                    for bitInfo in fieldInfo.bitfieldInfo:
                        ret += add_param(bitInfo.name, str(Messaging.get(self, bitInfo)))
            else:
                arrayList = []
                terminate = 0
                for i in range(0,fieldInfo.count):
                    arrayList.append(str(Messaging.get(self, fieldInfo, i)))
                ret += add_param(fieldInfo.name, "[" + ','.join(arrayList) + "]")
                if terminate:
                    break

        if ret.endswith(", "):
            ret = ret[:-2]
        return "%s(%s)" % (self.MsgName(), ret)

    # Accessors
    <ACCESSORS>

    # Reflection information
    fields = [ \
        <REFLECTION>\
    ]
