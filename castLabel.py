#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QMainWindow, QAction, QInputDialog, QFileDialog
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QSizePolicy
from PyQt5.QtWidgets import QPushButton, QLabel, QScrollArea
from PyQt5.QtGui import QIcon, QImage, QPixmap, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QPointF, QRect

import os
import os.path as osp
import json
import numpy as np


class CastLabel(QWidget):
    def __init__(self, parent):
        super(CastLabel, self).__init__()
        self.parent = parent

        # size policy
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

        # selected?
        self.isSelected = False
        self.seltectable = False

        # paint
        self._painter = QPainter()
        self.pixmap = QPixmap()
        self.default_img = './img/cast_default.png'
        self.reset_pixmp(self.default_img)

    def heightForWidth(self, width):
        return width * 1.5

    def reset_pixmp(self, img_file=None):
        if img_file is None:
            qimg = QImage(self.default_img)
        else:
            qimg = QImage(img_file)
        self.pixmap = QPixmap.fromImage(qimg)

    def paintEvent(self, e):
        """paint event"""
        # print('paint event called')
        painter = self._painter
        painter.begin(self)

        # -- for better display
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # -- draw pixmap
        painter.drawPixmap(self.rect(), self.pixmap)

        # -- draw rect
        if self.isSelected:
            painter.setPen(QPen(QColor(200, 0, 0), 12))
            painter.drawRect(self.rect())

        painter.end()

    def mousePressEvent(self, e):
        # -- if mouse left click
        if e.button() == Qt.LeftButton and self.seltectable:
            self.parent.clean_seltected()
            self.isSelected = True
            self.update()
            self.parent.seletected_changed()
        else:
            pass
