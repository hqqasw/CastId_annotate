#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QMainWindow, QAction, QInputDialog, QFileDialog, QProgressDialog
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QSizePolicy
from PyQt5.QtWidgets import QPushButton, QLabel, QScrollArea, QMessageBox
from PyQt5.QtGui import QIcon, QImage, QPixmap, QPainter, QColor, QPen, QFont
from PyQt5.QtCore import Qt, QPointF, QRect

import os
import os.path as osp
import json
import numpy as np
from datetime import datetime
import time


from proposalWindow import ProposalWindow
from castWindow import CastWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # constant
        self.LABELED_LIMIT = 50
        self.PROPOSAL_LIMIT = 40

        # variable
        self.labeler = None
        self.cast_list = []
        self.proposal_list = []
        self.active_cast = 0
        self.package_dir = './'

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

        # status bar
        self.statusBar().showMessage('Ready')

        # menu bar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openAction)

        # tool bar
        self.toolbar = self.addToolBar('打开')
        self.toolbar.addAction(openAction)

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
        # self.proposal_wid.setMinimumSize(100, 1500)
        self.proposal_scroll = QScrollArea()
        self.proposal_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.proposal_scroll.setWidget(self.proposal_wid)
        self.proposal_scroll.setAutoFillBackground(True)
        self.proposal_scroll.setWidgetResizable(True)

        # layout
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch(2)
        self.button_layout.addWidget(self.status_label, 6)
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
        self.showloginDialog()

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
        self.package_dir = QFileDialog.getExistingDirectory(self, "选取文件夹", ".")
        # waiting
        self.cast_wid.clean_seltected()
        self.active_cast = 0
        self.proposal_wid.clean_seltected()
        self.cast_wid.set_selected_idx(self.active_cast)
        self.cast_scroll.verticalScrollBar().setValue(0)
        self.proposal_scroll.verticalScrollBar().setValue(0)
        # read affinity matrix
        progress = QProgressDialog(self)
        progress.setWindowTitle('请稍等')
        progress.setLabelText('正在操作...')
        progress.setWindowModality(Qt.WindowModal)
        progress.setRange(0, 2)
        progress.setValue(1)
        debug_st = time.time()
        self.affinity_mat = np.load(os.path.join(self.package_dir, 'Label', 'proposal_affinity.npy'))
        print('load affinity: {:.2f}'.format(time.time()-debug_st))
        debug_st = time.time()
        self.affinity_mat = (self.affinity_mat).astype(np.float32) / 1000.0
        print('change affinity: {:.2f}'.format(time.time()-debug_st))
        progress.setValue(2)
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

    def cast_selected_changed(self):
        self.active_cast = self.cast_wid.get_seletectd_idx()
        self.update_proposal()
        self.update()

    def update_cast(self):
        # update cast
        self.cast_list = self.get_cast()
        self.cast_wid.set_selected_idx(self.active_cast)
        cast_img_list = [osp.join(self.package_dir, 'Label', 'cast', x+'.jpg') for x in self.cast_list]
        self.cast_wid.update_cast(cast_img_list)

    def update_proposal(self):
        # update proposal
        # debug_st = time.time()
        proposal_result = self.get_proposal(self.cast_list[self.active_cast])
        # print('\t get proposal time: {:.2f}'.format(float(time.time()-debug_st)))
        # debug_st = time.time()
        self.proposal_list = proposal_result['candidate']
        img_list, bbox_list = self.proposal2info(
            self.proposal_list, osp.join(self.package_dir, 'Image'))
        # print('\t porposal to info: {:.2f}'.format(float(time.time()-debug_st)))
        # debug_st = time.time()
        self.proposal_wid.update_proposal(img_list, bbox_list)
        # print('\t draw proposal: {:.2f}'.format(float(time.time()-debug_st)))
        # update status label
        status_label_text = '已完成： {:d} / {:d}'.format(proposal_result['num_labeled'], proposal_result['num_proposal'])
        self.status_label.setText(status_label_text)

    # key and button event
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def yes_button_clicked(self):
        pid = self.cast_list[self.active_cast]
        proposal_seltected_idx = self.proposal_wid.get_seletectd_idx()
        labeled_list = [self.proposal_list[x] for x in proposal_seltected_idx]
        # debug_st = time.time()
        self.update_assignment(pid, labeled_list, [], [], [], self.labeler)
        # print('assigment: {:.2f}'.format(float(time.time()-debug_st)))
        # debug_st = time.time()
        self.update_cast()
        # print('update cast: {:.2f}'.format(float(time.time()-debug_st)))
        # debug_st = time.time()
        self.update_proposal()
        # print('update proposal: {:.2f}'.format(float(time.time()-debug_st)))
        self.proposal_wid.clean_seltected()
        self.proposal_scroll.verticalScrollBar().setValue(0)
        self.update()

    def no_button_clicked(self):
        pid = self.cast_list[self.active_cast]
        proposal_seltected_idx = self.proposal_wid.get_seletectd_idx()
        reject_list = [self.proposal_list[x] for x in proposal_seltected_idx]
        self.update_assignment(pid, [], reject_list, [], [], self.labeler)
        self.update_cast()
        self.update_proposal()
        self.proposal_wid.clean_seltected()
        self.proposal_scroll.verticalScrollBar().setValue(0)
        self.update()

    def others_button_clicked(self):
        pid = self.cast_list[self.active_cast]
        proposal_seltected_idx = self.proposal_wid.get_seletectd_idx()
        others_list = [self.proposal_list[x] for x in proposal_seltected_idx]
        self.update_assignment(pid, [], [], others_list, [], self.labeler)
        self.update_cast()
        self.update_proposal()
        self.proposal_wid.clean_seltected()
        self.proposal_scroll.verticalScrollBar().setValue(0)
        self.update()

    def invalid_button_clicked(self):
        pid = self.cast_list[self.active_cast]
        proposal_seltected_idx = self.proposal_wid.get_seletectd_idx()
        invalid_list = [self.proposal_list[x] for x in proposal_seltected_idx]
        self.update_assignment(pid, [], [], [], invalid_list, self.labeler)
        self.update_cast()
        self.update_proposal()
        self.proposal_wid.clean_seltected()
        self.proposal_scroll.verticalScrollBar().setValue(0)
        self.update()

    # utilts
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
        meta_file_name = os.path.join(self.package_dir, 'Label', 'meta.json')
        with open(meta_file_name, 'r') as f:
            info = json.load(f)
        return info['cast']

    def get_proposal(self, pid):
        meta_file_name = os.path.join(self.package_dir, 'Label', 'meta.json')
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

        score_file_name = os.path.join(self.package_dir, 'Label', 'score_{:05d}.npy'.format(version))
        score_mat = np.load(score_file_name)
        # debug_st = time.time()
        num_labeled = 0
        num_labeled += (np.max(score_mat, axis=0) == score_positive).sum()
        num_labeled += (np.max(score_mat, axis=0) == score_negative).sum()
        num_labeled += (np.max(score_mat, axis=0) == score_invalid).sum()
        # print('\t\t count num labeled: {:.3f}'.format(float(time.time()-debug_st)))

        cast_map = {}
        for i, name in enumerate(name_cast):
            cast_map[name] = i
        proposal_map = {}
        for i, name in enumerate(name_proposal):
            proposal_map[name] = i

        # debug_st = time.time()
        pi = cast_map[pid]
        score_array = score_mat[pi]
        rank = np.argsort(-score_array)
        # print('\t\t ranking: {:.3f}'.format(float(time.time()-debug_st)))
        st = 0
        ed = 0
        # debug_st = time.time()
        for i, r in enumerate(rank):
            if score_array[r] >= score_positive:
                st = i+1
            if score_array[r] > score_negative:
                ed = i+1
        # print('\t\t get st & ed: {:.3f}'.format(float(time.time()-debug_st)))
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

    def update_assignment(self, pid, labeled_list, reject_list, others_list, invalid_list, labeler=None):
        meta_file_name = os.path.join(self.package_dir, 'Label', 'meta.json')
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

        # debug_st = time.time()
        score_file_name = os.path.join(self.package_dir, 'Label', 'score_{:05d}.npy'.format(version))
        score_mat = np.load(score_file_name)
        # print('\t load score mat time: {:.2f}'.format(time.time()-debug_st))

        cast_map = {}
        for i, name in enumerate(name_cast):
            cast_map[name] = i
        proposal_map = {}
        for i, name in enumerate(name_proposal):
            proposal_map[name] = i
        pi = cast_map[pid]

        # debug_st = time.time()
        if len(labeled_list) > 0:
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
        # print('\t update score mat time: {:.2f}'.format(time.time()-debug_st))

        if len(reject_list) > 0:
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

        version += 1

        # save score
        score_file_name = os.path.join(self.package_dir, 'Label', 'score_{:05d}'.format(version))
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
                'set_invalid': len(invalid_list)
            }
        }
        info['log'].append(new_log_info)
        with open(meta_file_name, 'w') as f:
            f.write(json.dumps(info, indent=2))
