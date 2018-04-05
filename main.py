# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import pyqtSignal, QObject, Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QToolTip, QPushButton,
                             QMessageBox, QDesktopWidget, QMainWindow,
                             QAction, qApp, QMenu, QFrame, QLabel, QLineEdit,
                             QHBoxLayout, QVBoxLayout, QSplitter,
                             QSizePolicy, QCheckBox, QComboBox)
from PyQt5.QtGui import (QIcon, QFont, QColor, QPainter, QPen, QBrush)

from utils import L2Dist
from curve import Curve


class Communications(QObject):
    updateStatusBar = pyqtSignal(str)
    updateSelectedPoint = pyqtSignal(str, str, str)
    cyclePoint = pyqtSignal(int)
    gotoPoint = pyqtSignal(int)
    reorderPoint = pyqtSignal(int)
    moveXPoint = pyqtSignal(int)
    moveXPointTo = pyqtSignal(int)
    moveYPoint = pyqtSignal(int)
    moveYPointTo = pyqtSignal(int)
    toggleHull = pyqtSignal(bool)
    toggleGuide = pyqtSignal(bool)
    addCurve = pyqtSignal(str)
    removeCurve = pyqtSignal(str)
    selectCurve = pyqtSignal(str)
    selectedCurveName = pyqtSignal(str)


class DrawingBoard(QFrame, QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.curves = {}
        self.activeCurve = None
        self.pointDragged = None
        self.pointSelected = None
        self.selectedX = None
        self.selectedY = None
        self.c = None

    def connectEvents(self, c):
        self.c = c

    def mousePressEvent(self, event):
        if self.activeCurve is not None:
            for (i, (x, y)) in enumerate(self.curves[self.activeCurve].points):
                if L2Dist(x + 5, y + 5, event.x(), event.y()) < 8:
                    self.pointDragged = i
                    self.selectedX = event.x()
                    self.selectedY = event.y()
            if self.pointDragged is None:
                self.curves[self.activeCurve].add_point(event.x(), event.y())
                self.selectedX = event.x()
                self.selectedY = event.y()
                self.pointSelected = self.curves[self.activeCurve].points_no - 1
        self.emitSignals()
        self.update()

    def mouseMoveEvent(self, event):
        x = event.x()
        y = event.y()
        text = "x: {0},  y: {1}".format(x, y)
        self.c.updateStatusBar.emit(text)
        if self.pointDragged is not None:
            distance = L2Dist(self.selectedX, self.selectedY, x, y)
            if distance > 5:
                self.pointSelected = None
                i = self.pointDragged
                self.curves[self.activeCurve].move_point_to(i, x - 5, y - 5)
                self.emitSignals()
                self.update()

    def mouseReleaseEvent(self, event):
        if self.pointSelected:
            distance = L2Dist(self.selectedX, self.selectedY,
                              event.x(), event.y())
            if distance < 5:
                self.pointDragged = None
        if self.pointDragged is not None:
            self.pointSelected = self.pointDragged
        self.pointDragged = None
        if self.activeCurve is not None:
            for (i, (x, y)) in enumerate(self.curves[self.activeCurve].points):
                if L2Dist(x + 5, y + 5, event.x(), event.y()) < 8:
                    self.pointSelected = i
                    self.selectedX = event.x()
                    self.selectedY = event.y()
        self.emitSignals()
        self.update()

    def cyclePoint(self, order):
        if self.curves[self.activeCurve].points_no > 0:
            self.pointSelected = (self.pointSelected + order)
            self.pointSelected %= self.curves[self.activeCurve].points_no
            self.emitSignals()
            self.update()

    def gotoPoint(self, pointId):
        points_no = self.curves[self.activeCurve].points_no
        if points_no > 0 and pointId < points_no:
            self.pointSelected = pointId
            self.emitSignals()
            self.update()

    def moveXPoint(self, newCoord):
        i = self.pointSelected
        self.curves[self.activeCurve].move_point_by(i, newCoord, 0)
        self.emitSignals()
        self.update()

    def moveXPointTo(self, newCoord):
        i = self.pointSelected
        self.curves[self.activeCurve].move_point_to(i, x=newCoord)
        self.emitSignals()
        self.update()

    def moveYPoint(self, newCoord):
        i = self.pointSelected
        self.curves[self.activeCurve].move_point_by(i, 0, newCoord)
        self.emitSignals()
        self.update()

    def moveYPointTo(self, newCoord):
        i = self.pointSelected
        self.curves[self.activeCurve].move_point_to(i, y=newCoord)
        self.emitSignals()
        self.update()

    def toggleHull(self, is_hull):
        self.curves[self.activeCurve].toggle_hull(is_hull)
        self.update()

    def toggleGuide(self, is_guide):
        self.curves[self.activeCurve].toggle_guide(is_guide)
        self.update()

    def addCurve(self, ctype):
        cname = "Curve {}".format(len(self.curves) + 1)
        self.curves[cname] = Curve(ctype=ctype)
        self.c.addCurve.emit(cname)
        self.selectCurve(cname)
        self.c.selectedCurveName.emit(cname)
        self.update()

    def addBCurve(self):
        self.addCurve('bezier')

    def addRBCurve(self):
        self.addCurve('rbezier')

    def addICurve(self):
        self.addCurve('interp')

    def addNSCurve(self):
        self.addCurve('nspline')

    def addPSCurve(self):
        self.addCurve('pspline')

    def removeCurve(self, cname):
        self.curves.pop(cname)
        self.update()

    def selectCurve(self, cname):
        self.activeCurve = cname
        self.pointSelected = None
        print(cname)
        self.update()

    def emitSignals(self):
        if self.pointSelected is not None:
            i = self.pointSelected
            point = self.curves[self.activeCurve].points[i]
            self.c.updateSelectedPoint.emit(str(i),
                                            str(point[0]),
                                            str(point[1]))

    def paintEvent(self, event):
        painter = QPainter(self)

        for curve_name in self.curves:
            self.curves[curve_name].make_plot()
            if self.activeCurve != curve_name:
                painter.setPen(QPen(QColor(120, 120, 120)))
                painter.drawPolyline(self.curves[curve_name].plot)

        if self.activeCurve is not None:
            print(self.curves[self.activeCurve].points)
            if self.curves[self.activeCurve].is_hull:
                painter.setPen(QPen(QColor(0, 0, 255)))
                painter.drawPolygon(self.curves[self.activeCurve].hull)
            if self.curves[self.activeCurve].is_guide:
                painter.setPen(QPen(QColor(255, 0, 0)))
                painter.drawPolyline(self.curves[self.activeCurve].guide)
            #  potem aktywna
            painter.setPen(QPen(QColor(0, 0, 0)))
            painter.drawPolyline(self.curves[self.activeCurve].plot)

            #  potem zaznaczone punkty
            if self.pointSelected is not None:
                painter.setPen(QPen(QColor(255, 0, 0)))
                x, y = self.curves[self.activeCurve].points[self.pointSelected]
                painter.drawRect(x, y, 10, 10)

            #  i same punkty
            painter.setPen(QPen(QColor(0, 0, 0)))
            painter.setBrush(QBrush(QColor(0, 154, 0)))
            for (i, (x, y)) in enumerate(self.curves[self.activeCurve].points):
                painter.drawEllipse(x, y, 10, 10)
                painter.drawText(x + 10, y + 20, str(i))


class ParamFrame(QFrame):
    def __init__(self, parent, label):
        super().__init__(parent)
        frameLabel = QLabel(label)
        self.textField = QLineEdit("000000", self)
        self.textField.setSizePolicy(QSizePolicy.Expanding,
                                     QSizePolicy.Fixed)
        self.textField.setStyleSheet("QWidget { background-color: %s }" %
                                     QColor(255, 255, 255).name())
        self.plus1 = QPushButton("+1", self)
        self.plus1.setFixedWidth(23)
        self.plus1.setSizePolicy(QSizePolicy.Maximum,
                                 QSizePolicy.Preferred)
        self.minus1 = QPushButton("-1", self)
        self.minus1.setFixedWidth(23)
        layout = QHBoxLayout()
        layout.addStretch(1)
        layout.addWidget(frameLabel)
        layout.addWidget(self.textField)
        layout.addWidget(self.plus1)
        layout.addWidget(self.minus1)
        self.setLayout(layout)


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


class MainWidget(QMainWindow):
    def __init__(self):
        QWidget.__init__(self)
        self.c = Communications()
        self.initUI()

    def initUI(self):
        QToolTip.setFont(QFont('Lato', 12))

        # SET UP THE WINDOW
        homeWidget = QWidget()
        self.setCentralWidget(homeWidget)
        self.statusBar().showMessage('Editor set and ready!')
        self.resize(800, 600)
        self.center()
        self.setWindowTitle('CurveMinator v0.0.5')
        self.setWindowIcon(QIcon('icon.jpg'))
        self.board = DrawingBoard(self)

        # TOP MENU
        menubar = self.menuBar()
        newAction = QAction('New', self)
        newAction.setShortcut('Ctrl+N')
        newAction.triggered.connect(self.flush)

        openAction = QAction('Open', self)
        openAction.setShortcut('Ctrl+O')

        exportMenu = QMenu('Export image', self)
        pngAction = QAction('PNG', self)
        jpgAction = QAction('JPG', self)
        exportMenu.addAction(pngAction)
        exportMenu.addAction(jpgAction)

        exitAction = QAction(QIcon('foxxo.jpg'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addMenu(exportMenu)
        fileMenu.addAction(exitAction)

        curveMenu = menubar.addMenu('New curve')
        interpAction = QAction('Interpolated curve', self)
        nSplineAction = QAction('N-Spline', self)
        pSplineAction = QAction('P-Spline', self)
        bezierAction = QAction('Bézier curve', self)
        ratBezierAction = QAction('Rational Bézier curve', self)
        curveMenu.addAction(interpAction)
        curveMenu.addAction(nSplineAction)
        curveMenu.addAction(pSplineAction)
        curveMenu.addAction(bezierAction)
        curveMenu.addAction(ratBezierAction)

        bezierAction.triggered.connect(self.board.addBCurve)
        ratBezierAction.triggered.connect(self.board.addRBCurve)
        interpAction.triggered.connect(self.board.addICurve)
        nSplineAction.triggered.connect(self.board.addNSCurve)
        pSplineAction.triggered.connect(self.board.addPSCurve)

        # SET UP DRAWING SPACE AND TOOLBAR
        mainLayout = QHBoxLayout()

        self.board.setStyleSheet("QWidget { background-color: %s }" %
                                 QColor(255, 255, 255).name())
        self.board.setSizePolicy(QSizePolicy.Expanding,
                                 QSizePolicy.Expanding)
        self.functionBar = FunctionBar(self)

        self.functionBar.setFixedWidth(250)
        self.functionBar.setStyleSheet("QWidget { background-color: %s }" %
                                       QColor(128, 128, 128).name())
        self.functionBar.setSizePolicy(QSizePolicy.Fixed,
                                       QSizePolicy.Expanding)
        mainLayout.addWidget(self.board)
        mainLayout.addWidget(self.functionBar)
        homeWidget.setLayout(mainLayout)
        self.c.updateStatusBar.connect(self.updateStatusBar)
        self.c.updateSelectedPoint.connect(self.functionBar.updateSelectedPoint)
        self.c.cyclePoint.connect(self.board.cyclePoint)
        self.c.gotoPoint.connect(self.board.gotoPoint)
        self.c.moveXPoint.connect(self.board.moveXPoint)
        self.c.moveXPointTo.connect(self.board.moveXPointTo)
        self.c.moveYPoint.connect(self.board.moveYPoint)
        self.c.moveYPointTo.connect(self.board.moveYPointTo)
        self.c.toggleHull.connect(self.board.toggleHull)
        self.c.toggleGuide.connect(self.board.toggleGuide)
        self.c.addCurve.connect(self.functionBar.addCurve)
        self.c.removeCurve.connect(self.board.removeCurve)
        self.c.selectCurve.connect(self.board.selectCurve)
        self.c.selectedCurveName.connect(self.functionBar.selectedCurveName)
        self.board.connectEvents(self.c)
        self.functionBar.connectEvents(self.c)
        self.show()

    def updateStatusBar(self, text):
        self.statusBar().showMessage(text)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Confirm',
                                     "Do you really wish to quit?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def flush(self):
        pass


def main():
    app = QApplication(sys.argv)

    widget = MainWidget()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
