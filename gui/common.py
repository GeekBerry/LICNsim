from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


def HotColor(value):
    color = QColor()
    color.setHsvF(0.3 * (1 - value), 1.0, 1.0)  # 0.3为绿色; 0.0为红色
    return color


def DeepColor(value, color=QColor(Qt.red)):  # h:0.0为红色
    h, s, v, a = color.getHsvF()
    return QColor.fromHsvF(h, value, v, a)


# ================================================================================
class UIFrom:
    def __init__(self, UI_From):
        """
        :param UI_From: 要使用的 UI_From 类名
        """
        self.UI_From = UI_From

    def __call__(self, cls):
        def creater(parent, *args, **kwargs):
            widget = cls.__new__(cls, parent)
            super(cls, widget).__init__(parent)
            widget.ui = self.UI_From()
            widget.ui.setupUi(widget)
            widget.__init__(parent, *args, **kwargs)
            return widget

        return creater

