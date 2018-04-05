# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QPushButton, QFrame, QLabel, QLineEdit,
                             QHBoxLayout, QSizePolicy)
from PyQt5.QtGui import QColor


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
