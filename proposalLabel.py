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


class ProposalLabel(QWidget):
    def __init__(self, parent):
        super(ProposalLabel, self).__init__()
        self.parent = parent

        # size policy
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

        # selected?
        self.isSelected = False
        self.selectable = False

        # paint
        self._painter = QPainter()
        self.pixmap = QPixmap()
        self.default_img = './img/proposal_default.png'
        self.reset_pixmp(self.default_img)

    def heightForWidth(self, width):
        return width * 0.6

    def reset_pixmp(self, img_file=None, bbox=None):
        if img_file is None:
            qimg = QImage(self.default_img)
        else:
            qimg = QImage(img_file)
        if bbox is not None:
            rectpainter = QPainter()
            rectpainter.begin(qimg)
            rectpainter.setPen(QPen(QColor(0, 200, 0), 8))
            rectpainter.drawRect(bbox)
            rectpainter.end()
            # TODO: draw bbox
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
            painter.setPen(QPen(QColor(200, 0, 0), 15))
            painter.drawRect(self.rect())

        painter.end()

    def mousePressEvent(self, e):
        # -- if mouse left click
        if e.button() == Qt.LeftButton and self.selectable:
            self.isSelected = not self.isSelected
            self.update()
        else:
            pass