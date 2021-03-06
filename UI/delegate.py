#!/usr/bin/python
# -*- coding: utf-8 -*-

###############################################################################
# Module to implement delegate special editiing in tables
#   -CellEditor
#   -SpinEditor
#   -CheckEditor
#   -SpinEditor
#   -LineStyleDelegate
#   -comboLine
###############################################################################


import os
from PyQt4 import QtCore, QtGui


class CellEditor(QtGui.QItemDelegate):
    """Numeric editor of tableitem, with numeric validator"""
    def __init__(self, parent=None):
        super(CellEditor, self).__init__(parent)

    def createEditor(self, parent, option, index):
        widget = QtGui.QLineEdit(parent)
        widget.setAlignment(QtCore.Qt.AlignRight)
        widget.setValidator(QtGui.QDoubleValidator(self))
        return widget


class SpinEditor(QtGui.QItemDelegate):
    """Spinbox editor for tableitem"""
    def __init__(self, parent=None):
        super(SpinEditor, self).__init__(parent)

    def createEditor(self, parent, option, index):
        widget = QtGui.QSpinBox(parent)
        widget.setAlignment(QtCore.Qt.AlignRight)
        widget.setMinimum(1)
        return widget


class CheckEditor(QtGui.QItemDelegate):
    """Checkbox editor for tableitem"""
    def __init__(self, parent=None):
        super(CheckEditor, self).__init__(parent)

    def createEditor(self, parent, option, index):
        widget = QtGui.QCheckBox(parent)
        return widget

    def setEditorData(self, editor, index):
        value = index.data(QtCore.Qt.DisplayRole).toBool()
        editor.setChecked(value)

    def setModelData(self, editor, model, index):
        value = editor.isChecked()
        model.setData(index, QtCore.QVariant(value), QtCore.Qt.DisplayRole)


class ComboEditor(QtGui.QItemDelegate):
    """Combobox Editor for tableitem"""
    def __init__(self, owner, items=None):
        super(ComboEditor, self).__init__(owner)
        self.setItems(items)

    def setItems(self, items):
        self.items = items

    def createEditor(self, parent, option, index):
        self.editor = QtGui.QComboBox(parent)
        self.editor.addItems(self.items)
        return self.editor

    def setEditorData(self, editor, index):
        value = unicode(index.data(QtCore.Qt.DisplayRole).toString())
        try:
            num = self.items.index(value)
        except ValueError:
            num = -1
        editor.setCurrentIndex(num)

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, QtCore.QVariant(value), QtCore.Qt.DisplayRole)


class LineStyleDelegate(QtGui.QItemDelegate):
    """Special combobox editor delegate for line Style"""
    def __init__(self, object, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)

    def paint(self, painter, option, index):
        data = index.model().data(index, QtCore.Qt.UserRole)
        if data.isValid() and data.toPyObject() is not None:
            data = data.toPyObject()
            print data
            painter.save()

            rect = option.rect
            rect.adjust(+5, 0, -5, 0)

            pen = QtGui.QPen()
            pen.setColor(QtCore.Qt.black)
            pen.setWidth(3)
            pen.setStyle(data)
            painter.setPen(pen)

            middle = (rect.bottom() + rect.top()) / 2
            painter.drawLine(rect.left(), middle, rect.right(), middle)
            painter.restore()

        else:
            QtGui.QItemDelegate.paint(self, painter, option, index)


class comboLine(QtGui.QComboBox):
    """Special combobox editor delegate for line Style"""
    def __init__(self, parent=None):
        QtGui.QComboBox.__init__(self, parent)
        lineas = [os.environ["pychemqt"]+"/images/button/solid_line.png",
                  os.environ["pychemqt"]+"/images/button/dot_line.png",
                  os.environ["pychemqt"]+"/images/button/dash_line.png",
                  os.environ["pychemqt"]+"/images/button/dash_dot_line.png",
                  os.environ["pychemqt"]+"/images/button/dash_dot_dot_line.png"]
        for i in lineas:
            self.addItem(QtGui.QIcon(QtGui.QPixmap(i)), "")
        self.setItemDelegate(LineStyleDelegate(self))

    def paintEvent(self, e):
        data = self.itemData(self.currentIndex(), QtCore.Qt.UserRole)
        if data.isValid() and data.toPyObject() is not None:
            data = data.toPyObject()
            p = QtGui.QStylePainter(self)
            p.setPen(self.palette().color(QtGui.QPalette.Text))

            opt = QtGui.QStyleOptionComboBox()
            self.initStyleOption(opt)
            p.drawComplexControl(QtGui.QStyle.CC_ComboBox, opt)

            painter = QtGui.QPainter(self)
            painter.save()

            rect = p.style().subElementRect(QtGui.QStyle.SE_ComboBoxFocusRect,
                                            opt, self)
            rect.adjust(+5, 0, -5, 0)

            pen = QtGui.QPen()
            pen.setColor(QtCore.Qt.black)
            pen.setWidth(3)
            pen.setStyle(data)
            painter.setPen(pen)

            middle = (rect.bottom() + rect.top()) / 2
            painter.drawLine(rect.left(), middle, rect.right(), middle)
#            painter.restore()

        else:
            QtGui.QComboBox.paintEvent(self, e)
