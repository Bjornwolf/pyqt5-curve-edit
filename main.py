# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QPointF
from PyQt5.QtWidgets import (QApplication, QWidget, QToolTip, QPushButton,
                             QMessageBox, QDesktopWidget, QMainWindow,
                             QAction, qApp, QMenu, QFrame, QLabel, QLineEdit,
                             QHBoxLayout, QVBoxLayout, QSplitter,
                             QSizePolicy)
from PyQt5.QtGui import (QIcon, QFont, QColor, QPainter, QPen, QBrush,
                         QPolygonF)


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


class DrawingBoard(QFrame, QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.curves = {'default': {'points': [], 'type': 'bezier'}}
        self.activeCurve = 'default'
        self.pointDragged = None
        self.pointSelected = None
        self.selectedX = None
        self.selectedY = None
        self.c = None

    def connectEvents(self, c):
        self.c = c

    def mousePressEvent(self, event):
        for (i, (x, y)) in enumerate(self.curves[self.activeCurve]['points']):
            if L2Dist(x + 5, y + 5, event.x(), event.y()) < 8:
                self.pointDragged = i
                self.selectedX = event.x()
                self.selectedY = event.y()
        if self.pointDragged is None:
            self.curves[self.activeCurve]['points'].append((event.x(),
                                                            event.y()))
            self.selectedX = event.x()
            self.selectedY = event.y()
            self.pointSelected = len(self.curves[self.activeCurve]['points'])
            self.pointSelected -= 1
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
                points = self.curves[self.activeCurve]['points']
                points = points[:i] + [(x - 5, y - 5)] + points[i+1:]
                self.curves[self.activeCurve]['points'] = points
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
        for (i, (x, y)) in enumerate(self.curves[self.activeCurve]['points']):
            if L2Dist(x + 5, y + 5, event.x(), event.y()) < 8:
                self.pointSelected = i
                self.selectedX = event.x()
                self.selectedY = event.y()
        self.emitSignals()
        self.update()

    def cyclePoint(self, order):
        points = self.curves[self.activeCurve]['points']
        if len(points) > 0:
            self.pointSelected = (self.pointSelected + order) % len(points)
            self.curves[self.activeCurve]['points'] = points
            self.emitSignals()
            self.update()

    def gotoPoint(self, pointId):
        points = self.curves[self.activeCurve]['points']
        if len(points) > 0 and pointId < len(points):
            self.pointSelected = pointId
            self.emitSignals()
            self.update()

    def moveXPoint(self, newCoord):
        points = self.curves[self.activeCurve]['points']
        i = self.pointSelected
        points[i] = (points[i][0] + newCoord, points[i][1])
        self.curves[self.activeCurve]['points'] = points
        self.emitSignals()
        self.update()

    def moveXPointTo(self, newCoord):
        points = self.curves[self.activeCurve]['points']
        i = self.pointSelected
        points = (newCoord, points[i][1])
        self.curves[self.activeCurve]['points'] = points
        self.emitSignals()
        self.update()

    def moveYPoint(self, newCoord):
        points = self.curves[self.activeCurve]['points']
        i = self.pointSelected
        points[i] = (points[i][0], points[i][1] + newCoord)
        self.curves[self.activeCurve]['points'] = points
        self.emitSignals()
        self.update()

    def moveYPointTo(self, newCoord):
        points = self.curves[self.activeCurve]['points']
        i = self.pointSelected
        points[i] = (points[i][0], newCoord)
        self.curves[self.activeCurve]['points'] = points
        self.emitSignals()
        self.update()

    def emitSignals(self):
        points = self.curves[self.activeCurve]['points']
        if self.pointSelected is not None:
            i = self.pointSelected
            self.c.updateSelectedPoint.emit(str(i),
                                            str(points[i][0]),
                                            str(points[i][1]))

    def paintEvent(self, event):
        painter = QPainter(self)
        conv = convex_hull(self.curves[self.activeCurve]['points'])
        polygon = QPolygonF()
        for (x, y) in conv:
            polygon.append(QPointF(x + 5, y + 5))
        painter.setPen(QPen(QColor(0, 0, 255)))
        painter.drawPolygon(polygon)

        if self.pointSelected is not None:
            painter.setPen(QPen(QColor(255, 0, 0)))
            x, y = self.curves[self.activeCurve]['points'][self.pointSelected]
            painter.drawRect(x, y, 10, 10)
        if self.curves[self.activeCurve]['type'] == 'bezier' and \
                len(self.curves[self.activeCurve]['points']) > 1:
            print("PRE BEZIER")
            print(self.curves[self.activeCurve]['points'])
            points = [deCasteljau(self.curves[self.activeCurve]['points'],
                                  0.001 * t) for t in range(1001)]
            bezierPoly = QPolygonF()
            for (x, y) in points:
                bezierPoly.append(QPointF(x + 5, y + 5))
            painter.setPen(QPen(QColor(0, 0, 0)))
            painter.drawPolyline(bezierPoly)
            print(self.curves[self.activeCurve]['points'])
        painter.setBrush(QBrush(QColor(0, 154, 0)))
        for (i, (x, y)) in enumerate(self.curves[self.activeCurve]['points']):
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
        lineLayout = QVBoxLayout()
        lineLayout.addWidget(phButton)
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
        self.setWindowTitle('CurveMinator v0.0.1')
        self.setWindowIcon(QIcon('icon.jpg'))

        # TOP MENU
        menubar = self.menuBar()
        newAction = QAction('New', self)
        newAction.setShortcut('Ctrl+N')
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
        splineAction = QAction('Spline', self)
        bezierAction = QAction('Bézier curve', self)
        curveMenu.addAction(interpAction)
        curveMenu.addAction(splineAction)
        curveMenu.addAction(bezierAction)

        # SET UP DRAWING SPACE AND TOOLBAR
        mainLayout = QHBoxLayout()

        self.board = DrawingBoard(self)
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

    def nukesArming(self, event):
        self.isNukesArmed = event
        if event:
            self.statusBar().showMessage('Nukes armed!')
        else:
            self.statusBar().showMessage('Nukes disarmed!')

    def nukeEvent(self, event):
        if self.isNukesArmed:
            self.nukesSent += 1
            self.statusBar().showMessage('Nukes sent: {0}'.format(
                self.nukesSent))
        else:
            self.statusBar().showMessage('Arm the nukes first!')


def L2Dist(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def convex_hull(points):
    """Computes the convex hull of a set of 2D points.

    Input: an iterable sequence of (x, y) pairs representing the points.
    Output: a list of vertices of the convex hull in counter-clockwise order,
            starting from the vertex with the lexicographically
            smallest coordinates.
    Implements Andrew's monotone chain algorithm. O(n log n) complexity.
    """

    # Sort the points lexicographically (tuples
    # are compared lexicographically).
    # Remove duplicates to detect the case we
    # have just one unique point.
    points = sorted(set(points))

    # Boring case: no points or a
    # single point, possibly repeated
    # multiple times.
    if len(points) <= 1:
        return points

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    # Last point of each list is omitted because it is repeated
    # at the beginning of the other list
    return lower[:-1] + upper[:-1]


def deCasteljau(points, t):
    return deCasteljauRat(points, [1.0] * len(points), t)


def deCasteljauRat(points, weights, t):
    cpPoints = [points[i] for i in range(len(points))]
    t1 = 1.0 - t
    for k in range(1, len(cpPoints) + 1):
        for i in range(len(cpPoints) - k):
            u = t1 * weights[i]
            v = t * weights[i + 1]
            weights[i] = u + v
            u = u / weights[i]
            v = 1 - u
            cpPoints[i] = combine_pairs([u, v], [cpPoints[i], cpPoints[i + 1]])
    return cpPoints[0]


def combine_pairs(weights, points):
    result = (0.0, 0.0)
    for (i, (x, y)) in enumerate(points):
        result = (result[0] + weights[i] * x, result[1] + weights[i] * y)
    return result


def main():
    app = QApplication(sys.argv)

    widget = MainWidget()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
