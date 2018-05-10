# -*- coding: utf-8 -*-

from PyQt5.QtCore import pyqtSignal, QObject


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
    renameCurve = pyqtSignal(str)
