# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QToolTip, QMessageBox,
                             QDesktopWidget, QMainWindow, QAction, qApp, QMenu,
                             QHBoxLayout, QSizePolicy)
from PyQt5.QtGui import (QIcon, QFont, QColor)

from drawing_board import DrawingBoard
from communications import Communications
from function_bar import FunctionBar


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
        pass  # TODO