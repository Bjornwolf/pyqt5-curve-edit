# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QPushButton,
                             QMessageBox,
                             QFrame, QLabel, QLineEdit,
                             QHBoxLayout, QVBoxLayout, QSplitter,
                             QCheckBox, QComboBox)
from PyQt5.QtGui import (QFont, QColor)

from param_frame import ParamFrame


class FunctionBar(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()
        self.c = None

    def connectEvents(self, c):
        self.c = c

    def updateSelectedPoint(self, id, x, y):
        self.pointIdField.setText(id)
        self.xFrame.textField.setText(x)
        self.yFrame.textField.setText(y)
        self.update()

    def initUI(self):
        phButton = QPushButton('Placeholder', self)
        phButton.setFont(QFont('Lato', 12))
        phButton.resize(phButton.sizeHint())
        self.cbox = QComboBox(self)
        self.hullBox = QCheckBox('Show hull', self)
        self.guideBox = QCheckBox('Show guide', self)
        lineLayout = QVBoxLayout()
        lineLayout.addWidget(phButton)
        lineLayout.addWidget(self.cbox)
        lineLayout.addWidget(self.hullBox)
        lineLayout.addWidget(self.guideBox)
        self.cbox.activated[str].connect(self.selectCurve)
        self.hullBox.stateChanged.connect(self.toggleHull)
        self.guideBox.stateChanged.connect(self.toggleGuide)
        lineZone = QFrame()
        lineZone.setLayout(lineLayout)

        centeredLabel = QFrame()
        centeredLayout = QHBoxLayout()
        centeredLayout.addStretch(1)
        cycleLabel = QLabel("Cycle points")
        cycleLabel.setFont(QFont('Lato', 12))
        centeredLayout.addWidget(cycleLabel)
        centeredLayout.addStretch(1)
        centeredLabel.setLayout(centeredLayout)

        self.prevPoint = QPushButton("<")
        self.prevPoint.setFixedWidth(23)
        self.prevPoint.resize(self.prevPoint.sizeHint())
        self.pointIdField = QLineEdit("1000", self)
        self.pointIdField.setStyleSheet("QWidget { background-color: %s }" %
                                        QColor(255, 255, 255).name())
        self.nextPoint = QPushButton(">")
        self.nextPoint.setFixedWidth(23)
        pointCyclerLayout = QHBoxLayout()
        pointCyclerLayout.addWidget(self.prevPoint)
        pointCyclerLayout.addWidget(self.pointIdField)
        pointCyclerLayout.addWidget(self.nextPoint)
        pointCyclerFrame = QFrame()
        pointCyclerFrame.setLayout(pointCyclerLayout)
        self.pointIdField.textEdited.connect(self.gotoPoint)
        self.prevPoint.clicked.connect(self.cyclePrev)
        self.nextPoint.clicked.connect(self.cycleNext)

        self.xFrame = ParamFrame(self, "X:")
        self.xFrame.textField.textEdited.connect(self.changeX)
        self.xFrame.plus1.clicked.connect(self.increaseX)
        self.xFrame.minus1.clicked.connect(self.reduceX)
        self.yFrame = ParamFrame(self, "Y:")
        self.yFrame.textField.textEdited.connect(self.changeY)
        self.yFrame.plus1.clicked.connect(self.increaseY)
        self.yFrame.minus1.clicked.connect(self.reduceY)

        self.deleteButton = QPushButton('Delete point', self)
        self.deleteButton.setFont(QFont('Lato', 12))

        pointLayout = QVBoxLayout()
        pointLayout.addStretch(1)
        pointLayout.addWidget(centeredLabel)
        pointLayout.addWidget(pointCyclerFrame)
        pointLayout.addWidget(self.xFrame)
        pointLayout.addWidget(self.yFrame)
        pointLayout.addWidget(self.deleteButton)
        pointZone = QFrame()
        pointZone.setLayout(pointLayout)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(lineZone)
        splitter.addWidget(pointZone)
        vbox = QVBoxLayout()
        vbox.addWidget(splitter)
        self.setLayout(vbox)
        self.show()

    def reduceX(self):
        self.c.moveXPoint.emit(-1)
        x = int(self.xFrame.textField.text())
        self.xFrame.textField.setText(str(x - 1))
        self.update()

    def increaseX(self):
        self.c.moveXPoint.emit(1)
        x = int(self.xFrame.textField.text())
        self.xFrame.textField.setText(str(x + 1))
        self.update()

    def changeX(self, text):
        self.c.moveXPointTo.emit(0 if text == '' else int(text))
        self.update()

    def reduceY(self):
        self.c.moveYPoint.emit(-1)
        y = int(self.xFrame.textField.text())
        self.yFrame.textField.setText(str(y - 1))
        self.update()

    def increaseY(self):
        self.c.moveYPoint.emit(1)
        y = int(self.yFrame.textField.text())
        self.yFrame.textField.setText(str(y + 1))
        self.update()

    def changeY(self, text):
        self.c.moveYPointTo.emit(0 if text == '' else int(text))
        self.update()

    def gotoPoint(self, text):
        self.c.gotoPoint.emit(0 if text == '' else int(text))
        self.update()

    def cyclePrev(self):
        self.c.cyclePoint.emit(-1)
        self.update()

    def cycleNext(self):
        self.c.cyclePoint.emit(1)
        self.update()

    def toggleHull(self, state):
        is_hull = True if state == Qt.Checked else False
        self.c.toggleHull.emit(is_hull)
        self.update()

    def toggleGuide(self, state):
        is_guide = True if state == Qt.Checked else False
        self.c.toggleGuide.emit(is_guide)
        self.update()

    def selectCurve(self, cname):
        self.c.selectCurve.emit(cname)
        self.update()

    def addCurve(self, cname):
        self.cbox.addItem(cname)
        self.update()

    def removeCurve(self, cname):
        self.cbox.removeItem(cname)

    def selectedCurveName(self, cname):
        self.cbox.setCurrentText(cname)
        self.update()
