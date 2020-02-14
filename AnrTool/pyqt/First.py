import sys

from PyQt5.QtWidgets import QApplication,QWidget,QToolTip,QMainWindow
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont
import pyqtgraph as pg
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        pg.setConfigOption('background', '#f0f0f0')
        pg.setConfigOption('foreground', 'd')
        self.setupUI(self)
        self.draw1()

class ToolTip(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        QToolTip.setFont(QFont('SansSerif', 12))
        self.setToolTip('今天是<b>星期五</b>')
        self.setGeometry(300,200,350,400)
        self.setWindowTitle('设置控制提示信息')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w=ToolTip()
    w.resize(400,200)
    w.move(300,300)
    w.setWindowTitle('haha')
    w.show()
    sys.exit(app.exec_())
