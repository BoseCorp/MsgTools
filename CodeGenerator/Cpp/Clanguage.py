import MsgParser
from MsgUtils import *

import language

language.namespace = "<MSGNAME>_"
language.firstParam = "m_data"
language.firstParamDecl = "char* m_data"
language.const = ""

enums = language.enums
accessors = language.accessors
declarations = language.declarations
initCode = language.initCode
