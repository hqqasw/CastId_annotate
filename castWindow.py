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
    def __init__(self, parent, mode='normal'):
        super().__init__()
        self.parent = parent
        self.mode = mode
        if self.mode == 'wide':
            self.MAX_CAST_NUM = 12
            self.num_col = 6
            self.num_row = 2
            self.cast_num = 12
        elif self.mode == 'long':
            self.MAX_CAST_NUM = 12
            self.cast_num = 12
        else:
            self.MAX_CAST_NUM = 10
            self.cast_num = 10
        self.cast_labels = [CastLabel(self) for i in range(self.MAX_CAST_NUM)]
        print('init Cast Window.')

        self.initUI()

    def initUI(self):
        if self.mode == 'wide':
            self.layout = QGridLayout()
            for i in range(self.num_col):
                self.layout.setColumnStretch(i, 1)
            for i in range(self.num_row):
                self.layout.setRowStretch(i, 1)
            positions = [(i, j) for i in range(self.num_row) for j in range(self.num_col)]
            for i in range(self.cast_num):
                if i < self.MAX_CAST_NUM:
                    self.layout.addWidget(self.cast_labels[i], *positions[i])
        else:
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
        if idx < self.cast_num and idx >= 0:
            self.cast_labels[idx].isSelected = True
        else:
            self.clean_seltected()
        self.update()

    def get_seletectd_idx(self):
        sidx = -1
        for i in range(self.cast_num):
            if self.cast_labels[i].isSelected:
                sidx = i
        return sidx
