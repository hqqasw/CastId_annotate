#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QMainWindow, QAction, QInputDialog, QFileDialog
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QSizePolicy, QMessageBox
from PyQt5.QtWidgets import QPushButton, QLabel, QScrollArea
from PyQt5.QtGui import QIcon, QImage, QPixmap, QPainter, QColor, QPen, QGuiApplication
from PyQt5.QtCore import Qt, QPointF, QRect

import os
import os.path as osp
import json
import numpy as np
import webbrowser


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
        self.default_img = osp.join('.', 'img', 'cast_default.png')
        self.reset_pixmp(self.default_img)
        self.img_file = None

    def heightForWidth(self, width):
        return width * 1.5

    def reset_pixmp(self, img_file=None):
        self.img_file = img_file
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
            painter.setPen(QPen(QColor(200, 0, 0), 18))
            painter.drawRect(self.rect())

        painter.end()

    def mousePressEvent(self, e):
        # -- if mouse left click
        if e.button() == Qt.LeftButton and self.seltectable:
            if QGuiApplication.keyboardModifiers() == Qt.NoModifier:
                self.parent.clean_seltected()
                self.isSelected = True
                self.update()
                self.parent.seletected_changed()
            elif QGuiApplication.keyboardModifiers() == Qt.ControlModifier:
                if self.img_file is not None:
                    pid = osp.splitext(osp.basename(self.img_file))[0]
                    print(pid)
                    if pid[:2] == 'nm':
                        url = 'https://www.imdb.com/name/' + pid
                        webbrowser.open_new_tab(url)
            elif QGuiApplication.keyboardModifiers() == Qt.ShiftModifier:
                if self.img_file is not None:
                    pid = osp.splitext(osp.basename(self.img_file))[0]
                    print(pid)
                    if pid[:2] == 'nm':
                        url = 'https://movie.douban.com/subject_search?search_text=' + pid
                        webbrowser.open_new_tab(url)
        else:
            pass
