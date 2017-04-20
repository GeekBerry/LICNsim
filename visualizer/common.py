import PyQt5.QtGui as QtGui


def threshold(min, value, max):
    if value<min: return min
    if value>max: return max
    return value


def HotColor(value):
    color= QtGui.QColor()
    color.setHsvF(0.3*(1-value), 1.0, 1.0)  # 0.3为绿色; 0.0为红色
    return color


def DeepColor(value, h= 0.0):  # h:0.0为红色
    color= QtGui.QColor()
    color.setHsvF(h, value, 1.0)
    return color


#=======================================================================================================================
class QtUiBase:
    def setupUi(self, UIForm):
        self.ui= UIForm()
        self.ui.setupUi(self)



#=======================================================================================================================
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

    def setTexts(self, *texts):
        for i, text in enumerate(texts):
            self.setText( i+1, str(text) )

    def clear(self):
        children= self.takeChildren()
        for child in children:
            child.clear()
        self.table.clear()


class HeadTreeItem(TreeItem):
    def __init__(self, parent, text, *texts):
        if not isinstance(parent, QTreeWidget):
            raise TypeError
        super().__init__(None, text)
        self.setTexts(*texts)
        self.burl= parent

    def __delitem__(self, key):
        if key in self.table:
            index= self.burl.indexOfTopLevelItem(self.table[key])
            item= self.burl.takeTopLevelItem(index)
            item.clear()

    def clear(self):
        self.burl.clear()


