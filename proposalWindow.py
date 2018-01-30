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

from proposalLabel import ProposalLabel


class ProposalWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.MAX_PROPOSAL_NUM = 100
        self.proposal_num = 100
        self.num_col = 4
        self.num_row = self.proposal_num // self.num_col
        if self.proposal_num % self.num_col > 0:
            self.num_row += 1
        self.proposal_labels = [ProposalLabel(self) for i in range(self.MAX_PROPOSAL_NUM)]
        print('init Proposal Window.')

        self.initUI()

    def initUI(self):
        self.layout = QGridLayout()
        for i in range(self.num_col):
            self.layout.setColumnStretch(i, 1)
        for i in range(self.num_row):
            self.layout.setRowStretch(i, 1)

        positions = [(i, j) for i in range(self.num_row) for j in range(self.num_col)]
        for i in range(self.proposal_num):
            if i < self.MAX_PROPOSAL_NUM:
                self.layout.addWidget(self.proposal_labels[i], *positions[i])
        self.setLayout(self.layout)

    def update_proposal(self, img_list, bbox_list):
        self.proposal_num = len(img_list)
        for i in range(self.proposal_num):
            self.proposal_labels[i].reset_pixmp(img_list[i], bbox_list[i])
            self.proposal_labels[i].selectable = True
        for i in range(self.proposal_num, self.MAX_PROPOSAL_NUM):
            self.proposal_labels[i].reset_pixmp()
            self.proposal_labels[i].selectable = False
        self.update()

    def clean_seltected(self):
        for i in range(self.proposal_num):
            self.proposal_labels[i].isSelected = False
            self.update()

    def get_seletectd_idx(self):
        sidx = []
        for i in range(self.proposal_num):
            if self.proposal_labels[i].isSelected:
                sidx.append(i)
        print('proposal:', sidx)
        return sidx
