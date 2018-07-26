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
import time

from frameLabel import FrameLabel


class FrameWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.MAX_FRAME_NUM = 5
        self.frame_labels = [FrameLabel(self) for i in range(self.MAX_FRAME_NUM)]
        print('init Frame Window.')

        self.initUI()

    def initUI(self):
        self.left_layout = QHBoxLayout()
        self.left_layout.addWidget(self.frame_labels[0])
        self.left_layout.addWidget(self.frame_labels[1])
        self.right_layout = QHBoxLayout()
        self.right_layout.addWidget(self.frame_labels[3])
        self.right_layout.addWidget(self.frame_labels[4])

        self.out_left_layout = QVBoxLayout()
        self.out_left_layout.addStretch(4)
        self.out_left_layout.addLayout(self.left_layout)
        self.out_left_layout.addStretch(4)
        self.out_right_layout = QVBoxLayout()
        self.out_right_layout.addStretch(4)
        self.out_right_layout.addLayout(self.right_layout)
        self.out_right_layout.addStretch(4)

        self.layout = QHBoxLayout()
        self.layout.addLayout(self.out_left_layout, 8)
        self.layout.addWidget(self.frame_labels[2], 12)
        self.layout.addLayout(self.out_right_layout, 8)
        # for i in range(self.MAX_FRAME_NUM):
        #     self.layout.addWidget(self.frame_labels[i])
        self.setLayout(self.layout)

    def update_frame(self, img_list, bbox_list, frame_idx):
        for i in range(self.MAX_FRAME_NUM):
            idx = frame_idx - 2 + i
            if idx < 0 or idx >= len(img_list):
                self.frame_labels[i].reset_pixmp()
                self.frame_labels[i].selectable = False
            else:
                self.frame_labels[i].reset_pixmp(img_list[idx], bbox_list[idx])
                self.frame_labels[i].selectable = True
        # self.frame_labels[2].isSelected = True
        self.update()
