from tab_base_class import TabBaseClass
from PyQt5.QtWidgets import QPushButton, QSpinBox, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QSpacerItem
from PyQt5.QtWidgets import QGraphicsScene, QFileDialog
from PyQt5.QtCore import QPoint, QRect, QSize
from PyQt5.QtGui import QImage, QPixmap, QColor, QPen, QBrush, QPainter, QIcon
from pathlib import Path
import PyPDF2
import pdf2image
from PIL import ImageQt, Image
import os

class PDFMerge(TabBaseClass):
    def __init__(self, parent):
        self.parent = parent
        self.pdf_files = []
        self.move_button_size = QSize(25, 25)

        self.frame_list = []
        self.up_button_list = []
        self.down_button_list = []

    def confirmUI(self, widgets):
        self.widgets = widgets
        self.widgets.MERGE_AddPDFButton.clicked.connect(self.load_new_pdf)

    def load_new_pdf(self):
        fname = QFileDialog.getOpenFileNames(self.parent, 'Open file',
                                            'C:/Users/Gilles/Downloads', "pdf files (*.pdf)")

        self.set_new_pdf(fname[0])

    def set_new_pdf(self, files):
        for file in files:
            self.pdf_files.append(file)

            up_down_layout = QVBoxLayout()
            up_button = QPushButton("\u2303")
            up_button.setFixedSize(self.move_button_size)
            down_button = QPushButton("\u2304")
            down_button.setFixedSize(self.move_button_size)

            up_button.clicked.connect(self.move_up)
            down_button.clicked.connect(self.move_down)

            self.up_button_list.append(up_button)
            self.down_button_list.append(down_button)

            up_down_layout.addWidget(up_button)
            up_down_layout.addWidget(down_button)

            up_down_layout.setSpacing(1)

            pdf_name = os.path.split(file)[1]
            label = QLabel(pdf_name)

            main_layout = QHBoxLayout()
            main_layout.setContentsMargins(0, 0, 0, 0)

            width = self.widgets.MERGE_LeftLayout.geometry().width()
            height = self.move_button_size.height() * 2 + 5


            new_frame = QFrame()
            new_frame.setContentsMargins(0, 0, 0, 0)
            new_frame.setFixedSize(QSize(width,height))
            new_frame.setLayout(main_layout)
            new_frame.setFrameStyle(QFrame.WinPanel | QFrame.Plain)

            self.frame_list.append(new_frame)

            main_layout.addLayout(up_down_layout)
            main_layout.addWidget(label)

            # because of spacer at the bottom
            self.widgets.MERGE_PDFsVLayout.insertWidget(len(self.up_button_list) - 1, new_frame)

    def move_up(self):
        sender = self.parent.sender()
        index = self.up_button_list.index(sender)
        if index != 0:
            self.swap(index, index - 1)

    def move_down(self):
        sender = self.parent.sender()
        index = self.down_button_list.index(sender)
        if index != len(self.down_button_list) - 1:
            self.swap(index, index + 1)

    def swap(self, index1, index2):
        # make index2 bigger then index1
        if index2 < index1:
            index1, index2 = index2, index1

        self.up_button_list[index1], self.up_button_list[index2] = self.up_button_list[index2], self.up_button_list[index1]
        self.down_button_list[index1], self.down_button_list[index2] = self.down_button_list[index2], self.down_button_list[index1]

        frame2 = self.widgets.MERGE_PDFsVLayout.takeAt(index2)
        frame1 = self.widgets.MERGE_PDFsVLayout.takeAt(index1)

        self.pdf_files[index1], self.pdf_files[index2] = self.pdf_files[index2], self.pdf_files[index1]

        self.widgets.MERGE_PDFsVLayout.insertWidget(index1, frame2.widget())
        self.widgets.MERGE_PDFsVLayout.insertWidget(index2, frame1.widget())

    def handle_resizing(self):
        pass