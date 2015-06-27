import MsgParser

# >/</= means big/little/native endian, see docs for struct.pack_into or struct.unpack_from.
def fieldType(field):
    fieldTypeDict = \
    {"uint64":">Q", "uint32":">L", "uint16": ">H", "uint8": "B",
      "int64":">q",  "int32":">l",  "int16": ">h",  "int8": "b",
      "float64":">d", "float32":">f"}
    typeStr = str.lower(field["Type"])
    return fieldTypeDict[typeStr]
    
def msgSize(msg):
    offset = 0
    for field in msg["Fields"]:
        offset += MsgParser.fieldSize(field) * MsgParser.fieldCount(field)
    return offset

def pythonFieldCount(field):
    count = MsgParser.fieldCount(field)
    if MsgParser.fieldUnits(field) == "ASCII" and (field["Type"] == "uint8" or field["Type"] == "int8"):
        count = 1
    return count

def reflectionInterfaceType(field):
    type = field["Type"]
    if "float" in type or "Offset" in field or "Scale" in field:
        type = "float"
    elif MsgParser.fieldUnits(field) == "ASCII" or "Enum" in field:
        type = "string"
    else:
        type = "int"
    return type

def fieldInfos(msg):
    fieldInfos = []
    for field in msg["Fields"]:
        fieldInfo = "FieldInfo("+\
                      'name="'+field["Name"] + '",'+\
                      'type="'+reflectionInterfaceType(field) + '",'+\
                      'units="'+MsgParser.fieldUnits(field) + '",'+\
                      'description="'+MsgParser.fieldDescription(field) + '",'+\
                      'get="'+"Get" + field["Name"] + '",'+\
                      'set="'+"Set" + field["Name"]  + '",'+\
                      'count='+str(pythonFieldCount(field)) + ')'

        fieldInfos.append(fieldInfo)
    return "\n".join(fieldInfos)

def fnHdr(field, count, name):
    param = "bytes"
    if str.find(name, "Set") == 0:
        param += ", value"
    if  count > 1:
        param += ", idx"
    ret = '''\
@staticmethod
@msg.units('%s')
@msg.default('%s')
@msg.count(%s)
def %s(%s):
    """%s"""''' % (MsgParser.fieldUnits(field), str(MsgParser.fieldDefault(field)), str(count), name, param, MsgParser.fieldDescription(field))
    return ret

def getFn(msg, field, offset):
    loc = msg["Name"] + ".MSG_OFFSET + " + str(offset)
    param = "bytes"
    type = fieldType(field)
    count = MsgParser.fieldCount(field)
    cleanup = ""
    if  count > 1:
        if MsgParser.fieldUnits(field) == "ASCII" and (field["Type"] == "uint8" or field["Type"] == "int8"):
            type = str(count) + "s"
            count = 1
            cleanup = '''ascii_len = str(value).find("\\\\x00")
    value = str(value)[2:ascii_len]
    ''' 
        else:
            loc += "+idx*" + str(MsgParser.fieldSize(field))
            param += ", idx"
    if "Offset" in field or "Scale" in field:
        cleanup = "value = " + MsgParser.getMath("value", field, "")+"\n    "
    ret = '''\
%s
    value = struct.unpack_from('%s', bytes, %s)[0]
    %sreturn value
''' % (fnHdr(field,count, "Get"+field["Name"]), type, loc, cleanup)
    return ret

def setFn(msg, field, offset):
    param = "bytes, value"
    loc = msg["Name"] + ".MSG_OFFSET + " + str(offset)
    count = MsgParser.fieldCount(field)
    type = fieldType(field)
    math = "tmp = " + MsgParser.setMath("value", field, "int")
    if count > 1:
        if MsgParser.fieldUnits(field) == "ASCII" and (field["Type"] == "uint8" or field["Type"] == "int8"):
            type = str(count) + "s"
            count = 1
            math = "tmp = value.encode('utf-8')"
        else:
            loc += "+idx*" + str(MsgParser.fieldSize(field))
            param += ", idx"
    ret  = '''\
%s
    %s
    struct.pack_into('%s', bytes, %s, tmp)
''' % (fnHdr(field,count, "Set"+field["Name"]), math, type, loc)
    return ret

def getBitsFn(field, bits, offset, bitOffset, numBits):
    access = "(Get%s(bytes) >> %s) & %s" % (field["Name"], str(bitOffset), MsgParser.Mask(numBits))
    access = MsgParser.getMath(access, bits, "float")
    ret  = '''\
%s
    return %s
''' % (fnHdr(bits,1,"Get"+field["Name"]+bits["Name"]), access)
    return ret

def setBitsFn(field, bits, offset, bitOffset, numBits):
    ret = '''\
%s
    Set%s(bytes, (Get%s(bytes) & ~(%s << %s)) | ((%s & %s) << %s))
''' % (fnHdr(bits,1,"Set"+field["Name"]+bits["Name"]), field["Name"], field["Name"], MsgParser.Mask(numBits), str(bitOffset), MsgParser.setMath("value", bits, "int"), MsgParser.Mask(numBits), str(bitOffset))
    return ret

def accessors(msg):
    gets = []
    sets = []
    
    offset = 0
    for field in msg["Fields"]:
        gets.append(getFn(msg, field, offset))
        sets.append(setFn(msg, field, offset))
        bitOffset = 0
        if "Bitfields" in field:
            for bits in field["Bitfields"]:
                numBits = bits["NumBits"]
                gets.append(getBitsFn(field, bits, offset, bitOffset, numBits))
                sets.append(setBitsFn(field, bits, offset, bitOffset, numBits))
                bitOffset += numBits
        offset += MsgParser.fieldSize(field) * MsgParser.fieldCount(field)

    return gets+sets

def initField(field, messageName):
    if "Default" in field:
        if "Enum" in field:
            return messageName + ".Set" + field["Name"] + "(bytes, " + messageName + "." + str(field["Enum"]) + "['" +str(field["Default"]) + "'])"
        else:
            return  messageName + ".Set" + field["Name"] + "(bytes, " + str(field["Default"]) + ")"
    return ""

def initBitfield(field, bits, messageName):
    if "Default" in bits:
        return  messageName + ".Set" + field["Name"] + bits["Name"] + "(bytes, " + str(bits["Default"]) + ")"
    return ""

def initCode(msg):
    ret = []
    
    offset = 0
    for field in msg["Fields"]:
        fieldInit = initField(field, msg["Name"])
        if fieldInit:
            ret.append(fieldInit)
        if "Bitfields" in field:
            for bits in field["Bitfields"]:
                bits = initBitfield(field, bits, msg["Name"])
                if bits:
                    ret.append(bits)

    return ret

def enums(e):
    ret = ""
    for enum in e:
        ret +=  enum["Name"]+" = {"
        for option in enum["Options"]:
            ret += '"'+option["Name"]+'"'+" : "+str(option["Value"]) + ', '
        ret = ret[:-2]
        ret += "}\n"
    return ret

def reflection(msg):
    return ""
