# -*- coding: utf-8 -*-

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QFrame
from PyQt5.QtGui import (QColor, QPainter, QPen, QBrush)

from utils import L2Dist
from curve import Curve


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

    def loadCurves(self, curves):
        self.curves = curves
        print(self.curves.keys())
        self.curves = curves
        self.activeCurve = list(self.curves.keys())[0]
        self.c.selectedCurveName.emit(self.activeCurve)
        self.pointDragged = None
        self.pointSelected = None
        self.selectedX = None
        self.selectedY = None
        self.update()

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
            print("zmejkplocony")
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
            print(self.curves[self.activeCurve].plot)
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
