#!/cygdrive/c/Python34/python.exe
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Messaging import Messaging

class FieldItem(QTreeWidgetItem):
    def __init__(self, msg_class, msg_buffer_wrapper, fieldInfo, column_strings = []):
        column_strings = column_strings if len(column_strings) > 0 else [None, fieldInfo.name, "", fieldInfo.units, fieldInfo.description]
        
        QTreeWidgetItem.__init__(self, None, column_strings)
        
        self.fieldInfo = fieldInfo
        self.msg_class = msg_class
        self.msg_buffer_wrapper = msg_buffer_wrapper
        
    def data(self, column, role):
        if column != 2:
            return super(FieldItem, self).data(column, role)

        alert = Messaging.getAlert(self.msg_buffer_wrapper["msg_buffer"], self.fieldInfo)
        if role == Qt.FontRole:
            font = QFont()
            if alert == 1:
                font.setBold(1)
            return font
        if role == Qt.ForegroundRole:
            brush = QBrush()
            if alert == 1:
                brush.setColor(Qt.red)
            return brush

        if role == Qt.DisplayRole:
            value  = Messaging.get(self.msg_buffer_wrapper["msg_buffer"], self.fieldInfo)
            
            try:
                self.overrideWidget
                valueAsString = Messaging.get(self.msg_buffer_wrapper["msg_buffer"], self.fieldInfo)
                
                if valueAsString in self.comboBoxIndexOfEnum:
                    #self.overrideWidget.setCurrentText(valueAsString)
                    self.overrideWidget.setCurrentIndex(self.comboBoxIndexOfEnum[valueAsString])
                else:
                    #self.overrideWidget.setEditText(valueAsString)
                    self.overrideWidget.setCurrentIndex(-1)
            except AttributeError:
                pass
                
            return str(value)
            
        return super(FieldItem, self).data(column, role)

class EditableFieldItem(FieldItem):
    def __init__(self, msg_class, msg_buffer_wrapper, fieldInfo, column_strings = []):
        super(EditableFieldItem, self).__init__(msg_class, msg_buffer_wrapper, fieldInfo, column_strings)

        self.setFlags(self.flags() | Qt.ItemIsEditable)
        
        if fieldInfo.type == "enumeration":
            self.overrideWidget = QComboBox()
            # if we need keys in order originally specified, it needs to be declared as an OrderedDict
            self.overrideWidget.addItems(sorted(list(fieldInfo.enum[0].keys())))
            self.overrideWidget.activated.connect(self.overrideWidgetValueChanged)
            # there's some odd behavior in the UI when the box is editable :(
            # if you want it editable, uncomment this line, and play around and see if you like it
            #self.overrideWidget.setEditable(1)
            # store a hash table of value->ComboBoxIndex
            # this is NOT the same as value->enumIndex!
            self.comboBoxIndexOfEnum = {}
            for i in range(0, self.overrideWidget.count()):
                self.comboBoxIndexOfEnum[self.overrideWidget.itemText(i)] = i

    def overrideWidgetValueChanged(self, value):
        valueAsString = self.overrideWidget.itemText(value)
        # set the value in the message/header buffer
        Messaging.set(self.msg_buffer_wrapper["msg_buffer"], self.fieldInfo, valueAsString)

        # no need to reset UI to value read from message, if user picked value from drop down.
        # \todo: need to if they type something, though.
        
    def setData(self, column, role, value):
        if not column == 2:
            return

        if self.fieldInfo.name == "ID":
            return
        
        if self.fieldInfo.type == "int" and value.startswith("0x"):
            value = str(int(value, 0))

        # set the value in the message/header buffer
        Messaging.set(self.msg_buffer_wrapper["msg_buffer"], self.fieldInfo, value)

        # get the value back from the message/header buffer and pass on to super-class' setData
        super(FieldItem, self).setData(column, role, Messaging.get(self.msg_buffer_wrapper["msg_buffer"], self.fieldInfo))

class FieldBits(FieldItem):
    def __init__(self, msg_class, msg_buffer_wrapper, bitfieldInfo):
       column_strings = [None, "    " + bitfieldInfo.name, "", bitfieldInfo.units, bitfieldInfo.description]
       super(FieldBits, self).__init__(msg_class, msg_buffer_wrapper, bitfieldInfo, column_strings)

class FieldBitfieldItem(FieldItem):
    def __init__(self, tree_widget, msg_class, msg_buffer_wrapper, fieldInfo):
        super(FieldBitfieldItem, self).__init__(msg_class, msg_buffer_wrapper, fieldInfo)

        for bitfieldInfo in fieldInfo.bitfieldInfo:
            bitfieldBitsItem = FieldBits(self.msg_class, self.msg_buffer_wrapper, bitfieldInfo)
            self.addChild(bitfieldBitsItem)

class EditableFieldBits(EditableFieldItem):
    def __init__(self, msg_class, msg_buffer_wrapper, bitfieldInfo):
       column_strings = [None, "    " + bitfieldInfo.name, "", bitfieldInfo.units, bitfieldInfo.description]
       super(EditableFieldBits, self).__init__(msg_class, msg_buffer_wrapper, bitfieldInfo, column_strings)

class EditableFieldBitfieldItem(EditableFieldItem):
    def __init__(self, tree_widget, msg_class, msg_buffer_wrapper, fieldInfo):
        super(EditableFieldBitfieldItem, self).__init__(msg_class, msg_buffer_wrapper, fieldInfo)

        for bitfieldInfo in fieldInfo.bitfieldInfo:
            bitfieldBitsItem = EditableFieldBits(self.msg_class, self.msg_buffer_wrapper, bitfieldInfo)
            self.addChild(bitfieldBitsItem)
            try:
                bitfieldBitsItem.overrideWidget
                tree_widget.setItemWidget(bitfieldBitsItem, 2, bitfieldBitsItem.overrideWidget)
            except AttributeError:
                pass

class FieldArrayItem(QTreeWidgetItem):
    def __init__(self, msg_class, msg_buffer_wrapper, fieldInfo, field_array_constructor, index = None):
        column_strings = [None, fieldInfo.name, "", fieldInfo.units, fieldInfo.description]
        
        if index != None:
            column_strings[1] = "    [" + str(index) + "]"
        
        QTreeWidgetItem.__init__(self, None, column_strings)
        
        self.fieldInfo = fieldInfo
        self.msg_class = msg_class
        self.msg_buffer_wrapper = msg_buffer_wrapper
        self.index = index

        if index == None:
            for i in range(0, self.fieldInfo.count):
                messageFieldTreeItem = field_array_constructor(self.msg_class, self.msg_buffer_wrapper, self.fieldInfo, field_array_constructor, i)
                self.addChild(messageFieldTreeItem)

    def data(self, column, role):
        if column != 2:
            return super(FieldArrayItem, self).data(column, role)

        if self.index == None:
            return ""

        alert = Messaging.getAlert(self.msg_buffer_wrapper["msg_buffer"], self.fieldInfo, self.index)
        if role == Qt.FontRole:
            font = QFont()
            if alert == 1:
                font.setBold(1)
            return font
        if role == Qt.ForegroundRole:
            brush = QBrush()
            if alert == 1:
                brush.setColor(Qt.red)
            return brush

        if role == Qt.DisplayRole:
            value  = Messaging.get(self.msg_buffer_wrapper["msg_buffer"], self.fieldInfo, self.index)
            return str(value)

        return super(FieldArrayItem, self).data(column, role)

class EditableFieldArrayItem(FieldArrayItem):
    def __init__(self, messageClass, msg_buffer_wrapper, fieldInfo, field_array_constructor, index = None):
        super(EditableFieldArrayItem, self).__init__(messageClass, msg_buffer_wrapper, fieldInfo, field_array_constructor, index)

        self.setFlags(self.flags() | Qt.ItemIsEditable)

    def setData(self, column, role, value):
        if self.index == None:
            return

        if column != 2:
            return

        if self.fieldInfo.name == "ID":
            return

        # set the value in the message/header buffer
        Messaging.set(self.msg_buffer_wrapper["msg_buffer"], self.fieldInfo, value, int(self.index))

        # get the value back from the message/header buffer and pass on to super-class' setData
        super(EditableFieldArrayItem, self).setData(column, role, Messaging.get(self.msg_buffer_wrapper["msg_buffer"], self.fieldInfo, int(self.index)))

class QObjectProxy(QObject):
    send_message = pyqtSignal(object)
    def __init__(self):
        QObject.__init__(self)

class MessageItem(QTreeWidgetItem):
    def __init__(self, msg_name, tree_widget, msg_class, msg_buffer,
                 child_constructor = FieldItem,
                 child_array_constructor = FieldArrayItem,
                 child_bitfield_constructor = FieldBitfieldItem):
        QTreeWidgetItem.__init__(self, None, [msg_name])
        
        self.qobjectProxy = QObjectProxy()

        self.tree_widget = tree_widget

        self.msg_class = msg_class
        self.msg_buffer_wrapper = { "msg_buffer": msg_buffer }

        self.setup_fields(tree_widget, child_constructor, child_array_constructor, child_bitfield_constructor)

        tree_widget.addTopLevelItem(self)
        tree_widget.resizeColumnToContents(0)
        self.setExpanded(True)

    def repaintAll(self):
        # Refresh the paint on the entire tree
        # TODO This is not a good solution!  We should refresh *only* the item that changed, not whole tree!
        region = self.tree_widget.childrenRegion()
        self.tree_widget.setDirtyRegion(region)

    def set_msg_buffer(self, msg_buffer):
        self.msg_buffer_wrapper["msg_buffer"] = msg_buffer
        self.repaintAll()

    def setup_fields(self, tree_widget, child_constructor, child_array_constructor, child_bitfield_constructor):
        headerTreeItemParent = QTreeWidgetItem(None, [ "Header" ])
        self.addChild(headerTreeItemParent)

        for headerFieldInfo in Messaging.hdr.fields:
            headerFieldTreeItem = child_constructor(Messaging.hdr, self.msg_buffer_wrapper, headerFieldInfo)
            headerTreeItemParent.addChild(headerFieldTreeItem)

        for fieldInfo in self.msg_class.fields:
            messageFieldTreeItem = None

            if fieldInfo.count == 1:
                if fieldInfo.bitfieldInfo != None:
                    messageFieldTreeItem = child_bitfield_constructor(tree_widget, self.msg_class, self.msg_buffer_wrapper, fieldInfo)
                else:
                    messageFieldTreeItem = child_constructor(self.msg_class, self.msg_buffer_wrapper, fieldInfo)
            else:
                messageFieldTreeItem = child_array_constructor(self.msg_class, self.msg_buffer_wrapper, fieldInfo, child_array_constructor)
            
            self.addChild(messageFieldTreeItem)
            try:
                messageFieldTreeItem.overrideWidget
                tree_widget.setItemWidget(messageFieldTreeItem, 2, messageFieldTreeItem.overrideWidget)
            except AttributeError:
                pass

class EditableMessageItem(MessageItem):

    def __init__(self, msg_name, tree_widget, msg_class, msg_buffer):
        super(EditableMessageItem, self).__init__(msg_name, tree_widget, msg_class, msg_buffer, EditableFieldItem, EditableFieldArrayItem, EditableFieldBitfieldItem)

        sendButton = QPushButton("Send", tree_widget)
        sendButton.autoFillBackground()
        sendButton.clicked.connect(lambda: self.qobjectProxy.send_message.emit(self.msg_buffer_wrapper["msg_buffer"]))
        tree_widget.setItemWidget(self, 4, sendButton)
