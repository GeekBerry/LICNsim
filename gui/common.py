from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


def HotColor(value):
    color= QColor()
    color.setHsvF(0.3*(1-value), 1.0, 1.0)  # 0.3为绿色; 0.0为红色
    return color


def DeepColor( value, color= QColor(Qt.red) ):  # h:0.0为红色
    h, s, v, a= color.getHsvF()
    return QColor.fromHsvF(h, value, v, a)


# ================================================================================
class UIFrom:
    def __init__(self, UI_From):
        """
        :param UI_From: 要使用的UI_From类名
        """
        self.UI_From= UI_From

    def __call__(self, cls):
        def creater(parent=None, *args, **kwargs):
            widget= cls.__new__(cls)
            super(cls, widget).__init__(parent)  # FIXME parent
            widget.ui= self.UI_From()
            widget.ui.setupUi(widget)
            cls.__init__(widget, parent, *args, **kwargs)
            return widget
        return creater


# ================================================================================
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


class TreeItem(QTreeWidgetItem):
    def __init__(self, parent, text):
        self.burl= self
        super().__init__(parent, [text])
        self.table= {}

    def __getitem__(self, key):
        if key in self.table:
            return self.table[key]
        else:
            self.table[key]= child= TreeItem(self.burl, str(key))
            return child

    def __delitem__(self, key):
        if key in self.table:
            index= self.indexOfChild(self.table[key])
            item= self.takeChild(index)
            item.clear()
            del self.table[key]

    def widget(self, column):
        self.treeWidget().itemWidget(self, column)

    def setWidget(self, column, widget):
        self.treeWidget().setItemWidget(self, column, widget)

    def setWidgets(self, *widgets):
        for col, widget in enumerate(widgets):
            self.setWidget(col+1, widget)

    def setTexts(self, *values):
        for col, value in enumerate(values):
            self.setText( col+1, str(value) )

    def clear(self):
        children= self.takeChildren()
        for child in children:
            child.clear()
        self.table.clear()


class TreeWidget(QTreeWidget):
    def __init__(self, *args):
        super().__init__(*args)
        self.table= {}

    def setHead(self, *values):
        for col, value in enumerate(values):
            self.headerItem().setText(col, str(value))

    def __getitem__(self, key):
        if key in self.table:
            return self.table[key]
        else:
            self.table[key]= child= TreeItem(self, str(key))
            return child

    def __delitem__(self, key):
        if key in self.table:
            index= self.indexOfTopLevelItem(self.table[key])
            item= self.takeTopLevelItem(index)
            item.clear()




