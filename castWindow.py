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

from castLabel import CastLabel


class CastWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.MAX_CAST_NUM = 10
        self.cast_num = 10
        self.cast_labels = [CastLabel(self) for i in range(self.MAX_CAST_NUM)]
        print('init Cast Window.')

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        for i in range(self.cast_num):
            self.layout.addWidget(self.cast_labels[i])
        self.setLayout(self.layout)

    def update_cast(self, cast_list):
        self.cast_num = len(cast_list)
        for i in range(self.cast_num):
            self.cast_labels[i].reset_pixmp(cast_list[i])
            self.cast_labels[i].seltectable = True
        for i in range(self.cast_num, self.MAX_CAST_NUM):
            self.cast_labels[i].reset_pixmp()
            self.cast_labels[i].seltectable = False
        self.update()

    def seletected_changed(self):
        self.parent.cast_selected_changed()

    def clean_seltected(self):
        for i in range(self.cast_num):
            self.cast_labels[i].isSelected = False
            self.update()

    def set_selected_idx(self, idx):
        if idx < self.cast_num:
            self.cast_labels[idx].isSelected = True
        self.update()

    def get_seletectd_idx(self):
        sidx = -1
        for i in range(self.cast_num):
            if self.cast_labels[i].isSelected:
                sidx = i
        print('cast:', sidx)
        return sidx
