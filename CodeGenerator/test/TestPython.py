#!/usr/bin/env python3
import unittest
import yaml
import sys
sys.path.append(".")
import MsgParser
sys.path.append("Python")
import language

class TestCpp(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        with open("test/TestCase1.yaml", 'r') as inputFile:
            self.msgIDL = inputFile.read()
        self.msgDict = yaml.load(self.msgIDL)

    def test_accessors(self):
        expected = []
        expected.append("""\
@staticmethod
@msg.units('m/s')
@msg.default('1')
@msg.count(1)
def GetFieldA(bytes):
    \"\"\"\"\"\"
    value = struct.unpack_from('>L', bytes, MsgA.MSG_OFFSET + 0)[0]
    return value
""")
        expected.append("""\
@staticmethod
@msg.units('')
@msg.default('')
@msg.count(1)
def GetFieldABitsA(bytes):
    \"\"\"\"\"\"
    return (GetFieldA(bytes) >> 0) & 0x7fffffff
""")
        expected.append("""\
@staticmethod
@msg.units('')
@msg.default('2')
@msg.count(1)
def GetFieldB(bytes):
    \"\"\"\"\"\"
    value = struct.unpack_from('>H', bytes, MsgA.MSG_OFFSET + 4)[0]
    return value
""")
        expected.append("""\
@staticmethod
@msg.units('')
@msg.default('3')
@msg.count(5)
def GetFieldC(bytes, idx):
    \"\"\"\"\"\"
    value = struct.unpack_from('B', bytes, MsgA.MSG_OFFSET + 6+idx*1)[0]
    return value
""")
        expected.append("""\
@staticmethod
@msg.units('')
@msg.default('')
@msg.count(1)
def GetFieldD(bytes):
    \"\"\"\"\"\"
    value = struct.unpack_from('B', bytes, MsgA.MSG_OFFSET + 11)[0]
    return value
""")
        expected.append("""\
@staticmethod
@msg.units('')
@msg.default('7.1')
@msg.count(1)
def GetFieldDBitsA(bytes):
    \"\"\"\"\"\"
    return (float((GetFieldD(bytes) >> 0) & 0xf) / 14.357)
""")
        expected.append("""\
@staticmethod
@msg.units('')
@msg.default('')
@msg.count(1)
def GetFieldDBitsB(bytes):
    \"\"\"\"\"\"
    return (GetFieldD(bytes) >> 4) & 0x7
""")
        expected.append("""\
@staticmethod
@msg.units('')
@msg.default('1')
@msg.count(1)
def GetFieldDBitsC(bytes):
    \"\"\"\"\"\"
    return (GetFieldD(bytes) >> 7) & 0x1
""")
        expected.append("""\
@staticmethod
@msg.units('')
@msg.default('3.14159')
@msg.count(1)
def GetFieldE(bytes):
    \"\"\"\"\"\"
    value = struct.unpack_from('>f', bytes, MsgA.MSG_OFFSET + 12)[0]
    return value
""")
        expected.append("""\
@staticmethod
@msg.units('')
@msg.default('3.14')
@msg.count(1)
def GetFieldF(bytes):
    \"\"\"\"\"\"
    value = struct.unpack_from('>H', bytes, MsgA.MSG_OFFSET + 16)[0]
    value = ((value / 2.7) + 1.828)
    return value
""")
        expected.append("""\
@staticmethod
@msg.units('m/s')
@msg.default('1')
@msg.count(1)
def SetFieldA(bytes, value):
    \"\"\"\"\"\"
    tmp = value
    struct.pack_into('>L', bytes, MsgA.MSG_OFFSET + 0, tmp)
""")
        expected.append("""\
@staticmethod
@msg.units('')
@msg.default('')
@msg.count(1)
def SetFieldABitsA(bytes, value):
    \"\"\"\"\"\"
    SetFieldA(bytes, (GetFieldA(bytes) & ~(0x7fffffff << 0)) | ((value & 0x7fffffff) << 0))
""")
        expected.append("""\
@staticmethod
@msg.units('')
@msg.default('2')
@msg.count(1)
def SetFieldB(bytes, value):
    \"\"\"\"\"\"
    tmp = value
    struct.pack_into('>H', bytes, MsgA.MSG_OFFSET + 4, tmp)
""")
        expected.append("""\
@staticmethod
@msg.units('')
@msg.default('3')
@msg.count(5)
def SetFieldC(bytes, value, idx):
    \"\"\"\"\"\"
    tmp = value
    struct.pack_into('B', bytes, MsgA.MSG_OFFSET + 6+idx*1, tmp)
""")
        expected.append("""\
@staticmethod
@msg.units('')
@msg.default('')
@msg.count(1)
def SetFieldD(bytes, value):
    \"\"\"\"\"\"
    tmp = value
    struct.pack_into('B', bytes, MsgA.MSG_OFFSET + 11, tmp)
""")
        expected.append("""\
@staticmethod
@msg.units('')
@msg.default('7.1')
@msg.count(1)
def SetFieldDBitsA(bytes, value):
    \"\"\"\"\"\"
    SetFieldD(bytes, (GetFieldD(bytes) & ~(0xf << 0)) | ((int(value * 14.357) & 0xf) << 0))
""")
        expected.append("""\
@staticmethod
@msg.units('')
@msg.default('')
@msg.count(1)
def SetFieldDBitsB(bytes, value):
    \"\"\"\"\"\"
    SetFieldD(bytes, (GetFieldD(bytes) & ~(0x7 << 4)) | ((value & 0x7) << 4))
""")
        expected.append("""\
@staticmethod
@msg.units('')
@msg.default('1')
@msg.count(1)
def SetFieldDBitsC(bytes, value):
    \"\"\"\"\"\"
    SetFieldD(bytes, (GetFieldD(bytes) & ~(0x1 << 7)) | ((value & 0x1) << 7))
""")
        expected.append("""\
@staticmethod
@msg.units('')
@msg.default('3.14159')
@msg.count(1)
def SetFieldE(bytes, value):
    \"\"\"\"\"\"
    tmp = value
    struct.pack_into('>f', bytes, MsgA.MSG_OFFSET + 12, tmp)
""")
        expected.append("""\
@staticmethod
@msg.units('')
@msg.default('3.14')
@msg.count(1)
def SetFieldF(bytes, value):
    \"\"\"\"\"\"
    tmp = int((value - 1.828) * 2.7)
    struct.pack_into('>H', bytes, MsgA.MSG_OFFSET + 16, tmp)
""")
        expCount = len(expected)
        observed = language.accessors(MsgParser.Messages(self.msgDict)[0])
        obsCount = len(observed)
        self.assertEqual(expCount, obsCount)
        
        for i in range(expCount):
            self.assertMultiLineEqual(expected[i], observed[i])
        with self.assertRaises(IndexError):
            language.accessors(MsgParser.Messages(self.msgDict)[1])

    def test_msgNames(self):
        expected = "MsgA"
        observed = MsgParser.msgName(MsgParser.Messages(self.msgDict)[0])
        self.assertMultiLineEqual(expected, observed)
        with self.assertRaises(IndexError):
            MsgParser.msgName(MsgParser.Messages(self.msgDict)[1])
    
    def test_enums(self):
        expected = 'EnumA = {"OptionA" : 1, "OptionB" : 2, "OptionC" : 4, "OptionD" : 5}\n'
        observed = language.enums(MsgParser.Enums(self.msgDict))
        self.assertMultiLineEqual(expected, observed)
    
    def test_initCode(self):
        messageName = MsgParser.Messages(self.msgDict)[0]["Name"]

        expected = []
        expected.append(messageName + ".SetFieldA(bytes, 1)")
        expected.append(messageName + ".SetFieldB(bytes, 2)")
        expected.append(messageName + ".SetFieldC(bytes, 3)")
        expected.append(messageName + ".SetFieldDBitsA(bytes, 7.1)")
        expected.append(messageName + ".SetFieldDBitsC(bytes, 1)")
        expected.append(messageName + ".SetFieldE(bytes, 3.14159)")
        expected.append(messageName + ".SetFieldF(bytes, 3.14)")

        expCount = len(expected)

        observed = language.initCode(MsgParser.Messages(self.msgDict)[0])
        
        obsCount = len(observed)
        
        self.assertEqual(expCount, obsCount)

        for i in range(expCount):
            self.assertMultiLineEqual(expected[i], observed[i])

        with self.assertRaises(IndexError):
            language.initCode(MsgParser.Messages(self.msgDict)[1])

if __name__ == '__main__':
    unittest.main()
