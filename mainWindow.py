#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QMainWindow, QAction, QInputDialog, QFileDialog, QProgressDialog
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QSizePolicy
from PyQt5.QtWidgets import QPushButton, QLabel, QScrollArea, QMessageBox, QSlider, QLineEdit
from PyQt5.QtGui import QIcon, QImage, QPixmap, QPainter, QColor, QPen, QFont, QIntValidator, QGuiApplication
from PyQt5.QtCore import Qt, QPointF, QRect

import os
import os.path as osp
import json
import numpy as np
from datetime import datetime
import time
import webbrowser

from castLabel import CastLabel
from proposalWindow import ProposalWindow
from castWindow import CastWindow
from frameWindow import FrameWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # constant
        self.LABELED_LIMIT = 20
        self.PROPOSAL_LIMIT = 40

        # variable
        self.labeler = None
        self.cast_list = []
        self.proposal_list = []
        self.frame_list = []
        self.active_cast = 0
        self.package_dir = './'
        self.mid = None

        self.initUI()

    def initUI(self):

        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('电影人物标注')
        self.setWindowIcon(QIcon('icon.png'))

        # action
        openAction = QAction(QIcon('./icons/open.png'), '打开', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('打开一个包')
        openAction.triggered.connect(self.open_package)

        visualAction = QAction(QIcon('./icons/visual.png'), '推荐模式', self)
        visualAction.setShortcut('Ctrl+R')
        visualAction.setStatusTip('推荐模式')
        visualAction.triggered.connect(self.convert2visual)

        temporalAction = QAction(QIcon('./icons/temporal.png'), '时序模式', self)
        temporalAction.setShortcut('Ctrl+T')
        temporalAction.setStatusTip('时序模式')
        temporalAction.triggered.connect(self.convert2temporal)

        checkAction = QAction(QIcon('./icons/check.png'), '检查模式', self)
        checkAction.setShortcut('Ctrl+C')
        checkAction.setStatusTip('检查模式')
        checkAction.triggered.connect(self.convert2check)

        # status bar
        self.statusBar().showMessage('Ready')

        # menu bar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openAction)
        ModeMenu = menubar.addMenu('&Mode')
        ModeMenu.addAction(visualAction)
        ModeMenu.addAction(temporalAction)
        ModeMenu.addAction(checkAction)

        # tool bar
        self.toolbar = self.addToolBar('maintb')
        self.toolbar.addAction(openAction)
        self.toolbar.addAction(visualAction)
        self.toolbar.addAction(temporalAction)
        self.toolbar.addAction(checkAction)

        # init mode as visual
        self.labeler = None
        self.mode = 'visual'  # mode: visual or temporal or check
        self.status = 'init'  # status: init or labeling

        # init visual UI
        self.init_visual_UI()

        self.showloginDialog()
        if len(self.labeler) > 0:
            self.setWindowTitle('电影人物标注 -- {}'.format(self.labeler))
        else:
            self.setWindowTitle('电影人物标注 -- 无名氏')

    def init_visual_UI(self):
        # main widget
        self.main_wid = QWidget()
        self.setCentralWidget(self.main_wid)

        # buttons
        button_font = QFont('Roman times', 16)
        self.yes_button = QPushButton('是他')
        self.yes_button.setFont(button_font)
        self.yes_button.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.yes_button.setEnabled(False)
        self.yes_button.setStyleSheet('background-color: green')
        self.yes_button.setStatusTip('是左边选中的这个演员')
        self.no_button = QPushButton('不是他')
        self.no_button.setFont(button_font)
        self.no_button.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.no_button.setEnabled(False)
        self.no_button.setStyleSheet('background-color: orange')
        self.no_button.setStatusTip('不是左边选中的这个演员')
        self.others_button = QPushButton('不是主演')
        self.others_button.setFont(button_font)
        self.others_button.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.others_button.setEnabled(False)
        self.others_button.setStyleSheet('background-color: red')
        self.others_button.setStatusTip('不是左边所有演员中的任何一个')
        self.invalid_button = QPushButton('框不明确')
        self.invalid_button.setFont(button_font)
        self.invalid_button.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.invalid_button.setEnabled(False)
        self.invalid_button.setStatusTip('框的不好，不知道框的是指哪个人')
        self.yes_button.clicked.connect(self.yes_button_clicked)
        self.no_button.clicked.connect(self.no_button_clicked)
        self.others_button.clicked.connect(self.others_button_clicked)
        self.invalid_button.clicked.connect(self.invalid_button_clicked)

        # status label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont('Roman times', 13))
        self.status_label.setText('已完成： */*')

        # mid label
        self.mid_label = QLabel()
        self.mid_label.setAlignment(Qt.AlignCenter)
        self.mid_label.setFont(QFont('Roman times', 15))
        self.mid_label.setStyleSheet('color: darkred')
        self.mid_label.setText('tt*****')
        self.mid_label.mousePressEvent = self.mid_labeld_clicked

        # cast window
        self.cast_wid = CastWindow(self)
        # self.cast_wid.setMinimumSize(100, 1500)
        self.cast_scroll = QScrollArea()
        self.cast_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cast_scroll.setWidgetResizable(True)
        self.cast_scroll.setWidget(self.cast_wid)
        self.cast_scroll.setAutoFillBackground(True)
        self.cast_scroll.setWidgetResizable(True)

        # proposal window
        self.proposal_wid = ProposalWindow(self)
        self.proposal_scroll = QScrollArea()
        self.proposal_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.proposal_scroll.setWidget(self.proposal_wid)
        self.proposal_scroll.setAutoFillBackground(True)
        self.proposal_scroll.setWidgetResizable(True)

        # layout
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch(2)
        self.button_layout.addWidget(self.mid_label, 3)
        self.button_layout.addWidget(self.status_label, 3)
        self.button_layout.addStretch(4)
        self.button_layout.addWidget(self.yes_button, 6)
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.no_button, 6)
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.others_button, 6)
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.invalid_button, 4)
        self.button_layout.addStretch(1)

        self.img_layout = QHBoxLayout()
        self.img_layout.addWidget(self.cast_scroll, 9)
        self.img_layout.addStretch(1)
        self.img_layout.addWidget(self.proposal_scroll, 50)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.img_layout, 48)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.button_layout, 4)
        self.main_layout.addStretch(1)

        # initial action
        self.main_wid.setLayout(self.main_layout)
        self.center()
        self.show()

    def init_temporal_UI(self):

        # main widget
        self.main_wid = QWidget()
        self.setCentralWidget(self.main_wid)
        self.main_wid.setFocusPolicy(Qt.StrongFocus)

        # slide
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.valueChanged.connect(self.slider_value_changed)
        self.slider.setEnabled(False)
        self.frame_num_label = QLabel(self)
        self.frame_num_label.setFont(QFont('Roman times', 13))
        self.frame_num_label.setText('/*')
        self.frame_idx_label = QLineEdit(self)
        self.frame_idx_label.setFont(QFont('Roman times', 13))
        self.frame_idx_label.setText('*')
        self.frame_idx_label.setValidator(QIntValidator())
        self.frame_idx_label.editingFinished.connect(self.frame_idx_changed)
        self.frame_idx_label.setEnabled(False)

        # status label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont('Roman times', 13))
        self.status_label.setText('已完成： */*')

        # mid label
        self.mid_label = QLabel()
        self.mid_label.setAlignment(Qt.AlignCenter)
        self.mid_label.setFont(QFont('Roman times', 15))
        self.mid_label.setStyleSheet('color: darkred')
        self.mid_label.setText('tt*****')
        self.mid_label.mousePressEvent = self.mid_labeld_clicked

        # cast window
        self.cast_wid = CastWindow(self, mode='wide')

        # Frame window
        self.frame_wid = FrameWindow(self)

        # seleted cast window
        self.selcast_wid = CastLabel(self)
        self.selcast_layout = QVBoxLayout()
        self.selcast_layout.addStretch(4)
        self.selcast_layout.addWidget(self.selcast_wid, 10)
        self.selcast_layout.addStretch(4)

        # layout
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch(2)
        self.button_layout.addWidget(self.mid_label, 3)
        self.button_layout.addWidget(self.status_label, 3)
        self.button_layout.addStretch(4)
        self.button_layout.addWidget(self.slider, 20)
        self.button_layout.addWidget(self.frame_idx_label, 4)
        self.button_layout.addWidget(self.frame_num_label, 4)
        self.button_layout.addStretch(2)

        self.cast_layout = QHBoxLayout()
        self.cast_layout.addStretch(2)
        self.cast_layout.addWidget(self.cast_wid, 30)
        self.cast_layout.addStretch(2)
        self.cast_layout.addLayout(self.selcast_layout, 8)
        self.cast_layout.addStretch(2)

        self.img_layout = QVBoxLayout()
        self.img_layout.addLayout(self.cast_layout, 18)
        self.img_layout.addStretch(1)
        self.img_layout.addWidget(self.frame_wid, 20)
        self.img_layout.addStretch(1)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.img_layout, 48)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.button_layout, 4)
        self.main_layout.addStretch(1)

        # initial action
        self.main_wid.setLayout(self.main_layout)
        self.center()
        self.show()

    def init_check_UI(self):
        # main widget
        self.main_wid = QWidget()
        self.setCentralWidget(self.main_wid)
        self.main_wid.setFocusPolicy(Qt.StrongFocus)

        # buttons
        button_font = QFont('Roman times', 16)
        self.error_button = QPushButton('标错了')
        self.error_button.setFont(button_font)
        self.error_button.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.error_button.setEnabled(False)
        self.error_button.setStyleSheet('background-color: red')
        self.error_button.setStatusTip('标注错误,点击之后该图片的标注将被清空')
        self.error_button.clicked.connect(self.error_button_clicked)

        # status label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont('Roman times', 13))
        self.status_label.setText('已完成： */*')

        # mid label
        self.mid_label = QLabel()
        self.mid_label.setAlignment(Qt.AlignCenter)
        self.mid_label.setFont(QFont('Roman times', 15))
        self.mid_label.setStyleSheet('color: darkred')
        self.mid_label.setText('tt*****')
        self.mid_label.mousePressEvent = self.mid_labeld_clicked

        # slider
        self.page_slider = QSlider(Qt.Horizontal)
        self.page_slider.setMinimum(0)
        self.page_slider.setMaximum(100)
        self.page_slider.valueChanged.connect(self.page_slider_value_changed)
        self.page_slider.setEnabled(False)
        self.page_num_label = QLabel(self)
        self.page_num_label.setFont(QFont('Roman times', 13))
        self.page_num_label.setText('/*')
        self.page_idx_label = QLineEdit(self)
        self.page_idx_label.setFont(QFont('Roman times', 13))
        self.page_idx_label.setText('*')
        self.page_idx_label.setValidator(QIntValidator())
        self.page_idx_label.editingFinished.connect(self.page_idx_changed)
        self.page_idx_label.setEnabled(False)

        # cast window
        self.cast_wid = CastWindow(self, mode='long')
        # self.cast_wid.setMinimumSize(100, 1500)
        self.cast_scroll = QScrollArea()
        self.cast_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cast_scroll.setWidgetResizable(True)
        self.cast_scroll.setWidget(self.cast_wid)
        self.cast_scroll.setAutoFillBackground(True)
        self.cast_scroll.setWidgetResizable(True)

        # proposal window
        self.proposal_wid = ProposalWindow(self, 20)
        self.proposal_scroll = QScrollArea()
        self.proposal_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.proposal_scroll.setWidget(self.proposal_wid)
        self.proposal_scroll.setAutoFillBackground(True)
        self.proposal_scroll.setWidgetResizable(True)

        # layout
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch(2)
        self.button_layout.addWidget(self.mid_label, 3)
        self.button_layout.addWidget(self.status_label, 3)
        self.button_layout.addStretch(2)
        self.button_layout.addWidget(self.page_slider, 10)
        self.button_layout.addWidget(self.page_idx_label, 4)
        self.button_layout.addWidget(self.page_num_label, 4)
        self.button_layout.addStretch(2)
        self.button_layout.addWidget(self.error_button, 6)
        self.button_layout.addStretch(2)

        self.img_layout = QHBoxLayout()
        self.img_layout.addWidget(self.cast_scroll, 9)
        self.img_layout.addStretch(1)
        self.img_layout.addWidget(self.proposal_scroll, 50)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.img_layout, 48)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.button_layout, 4)
        self.main_layout.addStretch(1)

        # initial action
        self.main_wid.setLayout(self.main_layout)
        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def showloginDialog(self):
        text, ok = QInputDialog.getText(self, '登录', '请输入你的名字')
        if ok:
            self.labeler = str(text)

    def open_package(self):
        new_package_dir = QFileDialog.getExistingDirectory(self, '选取文件夹', '.')
        if len(new_package_dir) < 1:
            return
        self.package_dir = new_package_dir
        if self.mode == 'temporal' or self.mode == 'check':
            self.mode = 'visual'
            self.init_visual_UI()
        # reset all UI
        self.cast_wid.clean_seltected()
        self.active_cast = 0
        self.proposal_wid.clean_seltected()
        self.cast_wid.set_selected_idx(self.active_cast)
        self.cast_scroll.verticalScrollBar().setValue(0)
        self.proposal_scroll.verticalScrollBar().setValue(0)
        # read affinity matrix
        self.statusBar().showMessage('读取数据中,请耐心等待...')
        if not (os.path.isdir(os.path.join(self.package_dir, 'label')) and os.path.isdir(os.path.join(self.package_dir, 'img'))):
            self.statusBar().showMessage('包错误！没有label或者img文件夹')
            return
        self.mid = self.package_dir.split('/')[-1]
        self.affinity_mat = np.load(os.path.join(self.package_dir, 'label', 'proposal_affinity.npy'))
        self.affinity_mat = (self.affinity_mat).astype(np.float32) / 1000.0
        self.statusBar().showMessage('读取数据成功')
        self.status = 'labeling'
        self.mid_label.setText(self.mid)
        # init cast
        self.update_cast()
        # init proposal
        self.update_proposal()
        # set button enable
        self.yes_button.setEnabled(True)
        self.no_button.setEnabled(True)
        self.others_button.setEnabled(True)
        self.invalid_button.setEnabled(True)
        self.update()

    def convert2visual(self):
        if self.mode != 'visual':
            self.cast_wid.clean_seltected()
            self.mode = 'visual'
            self.init_visual_UI()
            # reset all UI
            if self.status == 'labeling':
                self.mid_label.setText(self.mid)
                self.active_cast = 0
                self.proposal_wid.clean_seltected()
                self.cast_wid.set_selected_idx(self.active_cast)
                self.cast_scroll.verticalScrollBar().setValue(0)
                self.proposal_scroll.verticalScrollBar().setValue(0)
                self.update_cast()
                self.update_proposal()
                # set button enable
                self.yes_button.setEnabled(True)
                self.no_button.setEnabled(True)
                self.others_button.setEnabled(True)
                self.invalid_button.setEnabled(True)
                self.update()
        else:
            pass

    def convert2temporal(self):
        if self.mode != 'temporal':
            self.cast_wid.clean_seltected()
            self.mode = 'temporal'
            self.init_temporal_UI()
            self.active_frame = 0
            if self.status == 'labeling':
                self.mid_label.setText(self.mid)
                self.active_frame = 0
                self.update_frame()
                self.active_cast = self.label_list[self.active_frame]
                self.slider.setMaximum(len(self.label_list) - 1)
                self.frame_num_label.setText('/{}'.format(len(self.label_list) - 1))
                self.slider.setValue(0)
                self.frame_idx_label.setText('0')
                self.cast_wid.set_selected_idx(self.active_cast)
                self.update_cast()
                self.update_selcast()
                # set slider and lineedit enable
                self.slider.setEnabled(True)
                self.frame_idx_label.setEnabled(True)
                self.update()
        else:
            pass

    def convert2check(self):
        if self.mode != 'check':
            self.cast_wid.clean_seltected()
            self.mode = 'check'
            self.init_check_UI()
            # reset all UI
            if self.status == 'labeling':
                self.mid_label.setText(self.mid)
                self.active_cast = 0
                self.current_page = 0
                self.proposal_wid.clean_seltected()
                self.cast_wid.set_selected_idx(self.active_cast)
                self.cast_scroll.verticalScrollBar().setValue(0)
                self.proposal_scroll.verticalScrollBar().setValue(0)
                self.update_cast()
                self.update_labeled()
                # set button enable
                self.error_button.setEnabled(True)
                self.page_slider.setMaximum(self.total_pages-1)
                self.page_num_label.setText('/{}'.format(self.total_pages))
                self.page_slider.setValue(0)
                self.page_idx_label.setText('1')
                self.page_slider.setEnabled(True)
                self.page_idx_label.setEnabled(True)
                self.update()
        else:
            pass

    def cast_selected_changed(self):
        old_active_cast = self.active_cast
        self.active_cast = self.cast_wid.get_seletectd_idx()
        if self.mode == 'visual':
            self.update_proposal()
        elif self.mode == 'check':
            self.update_labeled()
            self.current_page = 0
            self.page_slider.setValue(0)
            self.page_num_label.setText('/{}'.format(self.total_pages))
            self.page_slider.setMaximum(self.total_pages-1)
            self.setFocus()
        else:
            if old_active_cast == self.active_cast:
                self.active_cast = -1
            self.update_selcast()
            self.cast_wid.set_selected_idx(self.active_cast)
            # update assignment
            if self.active_cast == len(self.cast_list):
                self.update_assignment(None, [], [], [self.frame_list[self.active_frame]], [], [], self.labeler)
            elif self.active_cast == len(self.cast_list) + 1:
                self.update_assignment(None, [], [], [], [self.frame_list[self.active_frame]], [], self.labeler)
            elif self.active_cast >= 0:
                self.update_assignment(self.cast_list[self.active_cast], [self.frame_list[self.active_frame]], [], [], [], [], self.labeler)
            elif self.active_cast == -1:
                self.update_assignment(None, [], [], [], [], [self.frame_list[self.active_frame]], self.labeler)
            # self.update_cast()
            self.update_frame()
        self.update()

    def update_cast(self):
        # update cast
        self.cast_list = self.get_cast()
        self.cast_wid.set_selected_idx(self.active_cast)
        cast_img_list = [osp.join(self.package_dir, 'label', 'cast', x+'.jpg') for x in self.cast_list]
        if self.mode == 'temporal' or self.mode == 'check':
            cast_img_list.append(osp.join('.', 'img', 'others.png'))
            cast_img_list.append(osp.join('.', 'img', 'invalid.png'))
        self.cast_wid.update_cast(cast_img_list)

    def update_proposal(self):
        proposal_result = self.get_proposal(self.cast_list[self.active_cast])
        self.proposal_list = proposal_result['candidate']
        img_list, bbox_list = self.proposal2info(
            self.proposal_list, osp.join(self.package_dir, 'img'))
        self.proposal_wid.update_proposal(img_list, bbox_list)
        status_label_text = '已完成： {:d} / {:d}'.format(proposal_result['num_labeled'], proposal_result['num_proposal'])
        self.status_label.setText(status_label_text)

    def update_labeled(self):
        self.proposal_wid.clean_seltected()
        if self.active_cast == len(self.cast_list):
            proposal_result = self.get_labeled('others')
        elif self.active_cast == len(self.cast_list) + 1:
            proposal_result = self.get_labeled('invalid')
        else:
            proposal_result = self.get_labeled(self.cast_list[self.active_cast])
        self.proposal_list = proposal_result['labeled']
        num_proposal = len(self.proposal_list)
        self.total_pages = num_proposal // self.LABELED_LIMIT
        if num_proposal % self.LABELED_LIMIT != 0:
            self.total_pages += 1
        st = self.current_page * self.LABELED_LIMIT
        ed = min((self.current_page + 1) * self.LABELED_LIMIT, num_proposal)
        img_list, bbox_list = self.proposal2info(
            self.proposal_list[st:ed], osp.join(self.package_dir, 'img'))
        self.proposal_wid.update_proposal(img_list, bbox_list)
        status_label_text = '已完成： {:d} / {:d}'.format(proposal_result['num_labeled'], proposal_result['num_proposal'])
        self.page_slider.setMaximum(self.total_pages-1)
        self.page_num_label.setText('/{}'.format(self.total_pages))
        if self.current_page >= self.total_pages:
            self.current_page = self.total_pages-1
            self.page_slider.setValue(self.total_pages-1)
            self.page_idx_label.setText('{}'.format(self.total_pages))
        self.status_label.setText(status_label_text)

    def update_frame(self):
        frame_result = self.get_frame()
        self.frame_list = frame_result['candidate']
        self.label_list = frame_result['labels']
        img_list, bbox_list = self.proposal2info(
            self.frame_list, osp.join(self.package_dir, 'img'))
        self.frame_wid.update_frame(img_list, bbox_list, self.active_frame)
        status_label_text = '已完成： {:d} / {:d}'.format(frame_result['num_labeled'], frame_result['num_proposal'])
        self.status_label.setText(status_label_text)

    def update_selcast(self):
        if self.active_cast < 0:
            self.selcast_wid.reset_pixmp()
        else:
            if self.active_cast == len(self.cast_list):
                img_name = osp.join('.', 'img', 'others.png')
            elif self.active_cast == len(self.cast_list) + 1:
                img_name = osp.join('.', 'img', 'invalid.png')
            else:
                img_name = osp.join(self.package_dir, 'label', 'cast', '{}.jpg'.format(self.cast_list[self.active_cast]))
            self.selcast_wid.reset_pixmp(img_name)

    # key and button event
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        if self.mode == 'temporal':
            if e.key() == Qt.Key_Right:
                if self.slider.value() < self.slider.maximum():
                    self.slider.setValue(self.slider.value() + 1)
            if e.key() == Qt.Key_Left:
                if self.slider.value() > 0:
                    self.slider.setValue(self.slider.value() - 1)
        elif self.mode == 'check':
            if e.key() == Qt.Key_Right:
                if self.page_slider.value() < self.page_slider.maximum():
                    self.page_slider.setValue(self.page_slider.value() + 1)
            if e.key() == Qt.Key_Left:
                if self.page_slider.value() > 0:
                    self.page_slider.setValue(self.page_slider.value() - 1)

    def yes_button_clicked(self):
        pid = self.cast_list[self.active_cast]
        proposal_seltected_idx = self.proposal_wid.get_seletectd_idx()
        labeled_list = [self.proposal_list[x] for x in proposal_seltected_idx]
        self.update_assignment(pid, labeled_list, [], [], [], [], self.labeler)
        self.update_cast()
        self.update_proposal()
        self.proposal_wid.clean_seltected()
        self.proposal_scroll.verticalScrollBar().setValue(0)
        self.update()

    def no_button_clicked(self):
        pid = self.cast_list[self.active_cast]
        proposal_seltected_idx = self.proposal_wid.get_seletectd_idx()
        reject_list = [self.proposal_list[x] for x in proposal_seltected_idx]
        self.update_assignment(pid, [], reject_list, [], [], [], self.labeler)
        self.update_cast()
        self.update_proposal()
        self.proposal_wid.clean_seltected()
        self.proposal_scroll.verticalScrollBar().setValue(0)
        self.update()

    def others_button_clicked(self):
        pid = self.cast_list[self.active_cast]
        proposal_seltected_idx = self.proposal_wid.get_seletectd_idx()
        others_list = [self.proposal_list[x] for x in proposal_seltected_idx]
        self.update_assignment(pid, [], [], others_list, [], [], self.labeler)
        self.update_cast()
        self.update_proposal()
        self.proposal_wid.clean_seltected()
        self.proposal_scroll.verticalScrollBar().setValue(0)
        self.update()

    def invalid_button_clicked(self):
        pid = self.cast_list[self.active_cast]
        proposal_seltected_idx = self.proposal_wid.get_seletectd_idx()
        invalid_list = [self.proposal_list[x] for x in proposal_seltected_idx]
        self.update_assignment(pid, [], [], [], invalid_list, [], self.labeler)
        self.update_cast()
        self.update_proposal()
        self.proposal_wid.clean_seltected()
        self.proposal_scroll.verticalScrollBar().setValue(0)
        self.update()

    def error_button_clicked(self):
        proposal_seltected_idx = self.proposal_wid.get_seletectd_idx()
        uncertain_list = [self.proposal_list[x+self.current_page*self.LABELED_LIMIT] for x in proposal_seltected_idx]
        self.update_assignment(None, [], [], [], [], uncertain_list, self.labeler)
        self.update_cast()
        self.update_labeled()
        self.proposal_wid.clean_seltected()
        self.proposal_scroll.verticalScrollBar().setValue(0)
        self.update()

    def slider_value_changed(self):
        self.active_frame = self.slider.value()
        self.update_frame()
        self.active_cast = self.label_list[self.active_frame]
        self.cast_wid.clean_seltected()
        self.cast_wid.set_selected_idx(self.active_cast)
        self.update_cast()
        self.update_selcast()
        self.frame_idx_label.setText('{}'.format(self.slider.value()))
        self.update()

    def frame_idx_changed(self):
        value = int(self.frame_idx_label.text())
        if value >= 0 and value < len(self.frame_list):
            self.slider.setValue(value)
        else:
            self.slider.setValue(self.slider.value())

    def page_slider_value_changed(self):
        self.current_page = self.page_slider.value()
        self.update_labeled()
        self.page_idx_label.setText('{}'.format(self.page_slider.value()+1))
        self.update()

    def page_idx_changed(self):
        value = int(self.page_idx_label.text()) - 1
        if value >= 0 and value < self.total_pages:
            self.page_slider.setValue(value)
        else:
            self.page_slider.setValue(self.page_slider.value())

    def mid_labeld_clicked(self, e):
        # -- if mouse left click
        if self.mid is not None and e.button() == Qt.LeftButton:
            if QGuiApplication.keyboardModifiers() == Qt.ControlModifier:
                url = 'https://www.imdb.com/title/' + self.mid
                webbrowser.open_new_tab(url)
            elif QGuiApplication.keyboardModifiers() == Qt.ShiftModifier:
                url = 'https://movie.douban.com/subject_search?search_text=' + self.mid
                webbrowser.open_new_tab(url)
        else:
            pass

    # utils
    def proposal2info(self, proposal_list, img_dir):
        img_list = []
        bbox_list = []
        for proposal in proposal_list:
            words = proposal.split('(')
            img_name = words[0][:-1]+'.jpg'
            img_path = osp.join(img_dir, img_name)
            bbox = self.str2bbox(words[1][:-1])
            img_list.append(img_path)
            bbox_list.append(bbox)
        return img_list, bbox_list

    def str2bbox(self, string):
        words = string.split(',')
        bbox = QRect(
            int(words[0]), int(words[1]),
            int(words[2])-int(words[0]),
            int(words[3])-int(words[1]))
        return bbox

    def get_cast(self):
        meta_file_name = os.path.join(self.package_dir, 'label', 'meta.json')
        with open(meta_file_name, 'r') as f:
            info = json.load(f)
        return info['cast']

    def get_labeled(self, pid):
        """
        for check mode
        get labeled proposals only
        """
        meta_file_name = os.path.join(self.package_dir, 'label', 'meta.json')
        with open(meta_file_name, 'r') as f:
            info = json.load(f)
        name_cast = info['cast']
        name_proposal = info['proposal']
        score_positive = info['score_positive']
        score_negative = info['score_negative']
        score_invalid = info['score_invalid']
        num_proposal = info['num_proposal']
        log_info = info['log'][-1]
        version = log_info['version']

        score_file_name = os.path.join(self.package_dir, 'label', 'score.npy')
        score_mat = np.load(score_file_name)
        max_score = np.max(score_mat, axis=0)
        num_labeled = 0
        num_labeled += (max_score == score_positive).sum()
        num_labeled += (max_score == score_negative).sum()
        num_labeled += (max_score == score_invalid).sum()

        cast_map = {}
        for i, name in enumerate(name_cast):
            cast_map[name] = i
        proposal_map = {}
        for i, name in enumerate(name_proposal):
            proposal_map[name] = i

        if pid == 'others':
            others_mask = (max_score == score_negative)
            rank_labeled = []
            for i in range(num_proposal):
                if others_mask[i]:
                    rank_labeled.append(i)
            rank_proposal = []
        elif pid == 'invalid':
            invalid_mask = (max_score == score_invalid)
            rank_labeled = []
            for i in range(num_proposal):
                if invalid_mask[i]:
                    rank_labeled.append(i)
            rank_proposal = []
        else:
            pi = cast_map[pid]
            score_array = score_mat[pi]
            rank = np.argsort(-score_array)
            st = 0
            ed = 0
            for i, r in enumerate(rank):
                if score_array[r] >= score_positive:
                    st = i+1
                if score_array[r] > score_negative:
                    ed = i+1
            rank_proposal = rank[st:ed]
            if len(rank_proposal) > self.PROPOSAL_LIMIT:
                rank_proposal = rank_proposal[:self.PROPOSAL_LIMIT]
            if st > 0:
                rank_labeled = rank[:st]
            else:
                rank_labeled = []

        result = {}
        result['labeled'] = [name_proposal[x] for x in rank_labeled]
        result['candidate'] = [name_proposal[x] for x in rank_proposal]
        result['num_proposal'] = int(num_proposal)
        result['num_labeled'] = int(num_labeled)
        return result

    def get_proposal(self, pid):
        """
        for visual mode
        get unlabeled proposals only
        """
        meta_file_name = os.path.join(self.package_dir, 'label', 'meta.json')
        with open(meta_file_name, 'r') as f:
            info = json.load(f)
        name_cast = info['cast']
        name_proposal = info['proposal']
        score_positive = info['score_positive']
        score_negative = info['score_negative']
        score_invalid = info['score_invalid']
        num_proposal = info['num_proposal']
        log_info = info['log'][-1]
        version = log_info['version']

        score_file_name = os.path.join(self.package_dir, 'label', 'score.npy')
        score_mat = np.load(score_file_name)
        max_score = np.max(score_mat, axis=0)
        num_labeled = 0
        num_labeled += (max_score == score_positive).sum()
        num_labeled += (max_score == score_negative).sum()
        num_labeled += (max_score == score_invalid).sum()

        cast_map = {}
        for i, name in enumerate(name_cast):
            cast_map[name] = i
        proposal_map = {}
        for i, name in enumerate(name_proposal):
            proposal_map[name] = i

        pi = cast_map[pid]
        score_array = score_mat[pi]
        rank = np.argsort(-score_array)
        st = 0
        ed = 0
        for i, r in enumerate(rank):
            if score_array[r] >= score_positive:
                st = i+1
            if score_array[r] > score_negative:
                ed = i+1
        rank_proposal = rank[st:ed]
        if len(rank_proposal) > self.PROPOSAL_LIMIT:
            rank_proposal = rank_proposal[:self.PROPOSAL_LIMIT]
        if st > 0:
            rank_labeled = rank[:st]
        else:
            rank_labeled = []
        if len(rank_labeled) > self.LABELED_LIMIT:
            tmp_idx = np.random.randint(0, len(rank_labeled), self.LABELED_LIMIT)
            rank_labeled = rank_labeled[tmp_idx]

        result = {}
        result['labeled'] = [name_proposal[x] for x in rank_labeled]
        result['candidate'] = [name_proposal[x] for x in rank_proposal]
        result['num_proposal'] = int(num_proposal)
        result['num_labeled'] = int(num_labeled)
        return result

    def get_frame(self):
        """
        for temporal mode
        get all proposals
        """
        meta_file_name = os.path.join(self.package_dir, 'label', 'meta.json')
        with open(meta_file_name, 'r') as f:
            info = json.load(f)
        name_cast = info['cast']
        name_proposal = info['proposal']
        score_positive = info['score_positive']
        score_negative = info['score_negative']
        score_invalid = info['score_invalid']
        num_proposal = int(info['num_proposal'])
        num_cast = int(info['num_cast'])
        log_info = info['log'][-1]
        version = log_info['version']

        score_file_name = os.path.join(self.package_dir, 'label', 'score.npy')
        score_mat = np.load(score_file_name)
        max_score = np.max(score_mat, axis=0)
        max_idx = np.argmax(score_mat, axis=0)
        positive_mask = (max_score == score_positive)
        negative_mask = (max_score == score_negative)
        invalid_mask = (max_score == score_invalid)
        # labels: -1: no annotation; 0-9: labeled as one of the cast; 10: others; 11: invalid
        labels = np.ones((num_proposal,), dtype=np.int16)*-1
        labels[positive_mask] = max_idx[positive_mask]
        labels[negative_mask] = num_cast
        labels[invalid_mask] = num_cast + 1
        num_labeled = 0
        num_labeled += positive_mask.sum()
        num_labeled += negative_mask.sum()
        num_labeled += invalid_mask.sum()

        result = {}
        result['labels'] = labels.tolist()
        result['candidate'] = name_proposal
        result['num_proposal'] = int(num_proposal)
        result['num_labeled'] = int(num_labeled)
        return result

    def update_assignment(self, pid, labeled_list, reject_list, others_list, invalid_list, uncertain_list, labeler=None):
        meta_file_name = os.path.join(self.package_dir, 'label', 'meta.json')
        with open(meta_file_name, 'r') as f:
            info = json.load(f)
        name_cast = info['cast']
        name_proposal = info['proposal']
        score_positive = info['score_positive']
        score_negative = info['score_negative']
        score_invalid = info['score_invalid']
        num_proposal = info['num_proposal']
        num_cast = info['num_cast']
        log_info = info['log'][-1]
        version = log_info['version']

        score_file_name = os.path.join(self.package_dir, 'label', 'score.npy')
        score_mat = np.load(score_file_name)

        cast_map = {}
        for i, name in enumerate(name_cast):
            cast_map[name] = i
        proposal_map = {}
        for i, name in enumerate(name_proposal):
            proposal_map[name] = i

        if len(labeled_list) > 0:
            pi = cast_map[pid]
            labeled_idx = [proposal_map[x] for x in labeled_list]
            tmp = np.zeros((num_proposal, 2))
            tmp[:, 0] = self.affinity_mat[labeled_idx, :].max(axis=0)
            tmp[:, 1] = score_mat[pi]
            reject_mask = (score_mat[pi] == score_negative)
            invalid_mask = (score_mat[pi] == score_invalid)
            tmp = tmp.max(axis=1)
            tmp[reject_mask] = score_negative
            tmp[invalid_mask] = score_invalid
            tmp[labeled_idx] = score_positive
            score_mat[:, labeled_idx] = score_negative
            score_mat[pi] = tmp

        if len(reject_list) > 0:
            pi = cast_map[pid]
            reject_idx = [proposal_map[x] for x in reject_list]
            tmp = score_mat[pi]
            tmp[reject_idx] = score_negative
            score_mat[pi] = tmp

        if len(others_list) > 0:
            others_idx = [proposal_map[x] for x in others_list]
            score_mat[:, others_idx] = score_negative

        if len(invalid_list) > 0:
            invalid_idx = [proposal_map[x] for x in invalid_list]
            score_mat[:, invalid_idx] = score_invalid

        if len(uncertain_list) > 0:
            uncertain_idx = [proposal_map[x] for x in uncertain_list]
            score_mat[:, uncertain_idx] = 0.1

        version += 1

        # save score
        score_file_name = os.path.join(self.package_dir, 'label', 'score')
        np.save(score_file_name, score_mat)

        # save meta
        new_log_info = {
            'version': version,
            'time_stamp': str(datetime.now()),
            'labeler': labeler,
            'update_info': {
                'set_positive': len(labeled_list),
                'set_negative': len(reject_list),
                'set_others': len(others_list),
                'set_invalid': len(invalid_list),
                'set_uncertain': len(uncertain_list)
            }
        }
        info['log'].append(new_log_info)
        with open(meta_file_name, 'w') as f:
            f.write(json.dumps(info, indent=2))
