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
            up_button = QPushButton("\u2304")
            up_button.setFixedSize(self.move_button_size)
            down_button = QPushButton("\u2303")
            down_button.setFixedSize(self.move_button_size)
            up_down_layout.addWidget(down_button)
            up_down_layout.addWidget(up_button)
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
            main_layout.addLayout(up_down_layout)
            main_layout.addWidget(label)

            self.widgets.MERGE_PDFsVLayout.addWidget(new_frame)

    def handle_resizing(self):
        pass