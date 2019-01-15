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
        self.widgets.MERGE_MergeButton.clicked.connect(self.merge_pdfs)

    def load_new_pdf(self):
        fname = QFileDialog.getOpenFileNames(self.parent, 'Open file',
                                            'C:/Users/Gilles/Downloads', "pdf files (*.pdf)")

        self.set_new_pdf(fname[0])

    def set_new_pdf(self, files):
        """
        Adds the files from the list onto the UI by creating the necessary buttons, layouts and Frames

        :param files: List of pdf names in the form of folder/filename.pdf
        :return: Nothing
        """
        for file in files:
            self.pdf_files.append(file)

            # This layout is used to place the up/down button on top of each other
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

            # The foldername isn't displayed on the label
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

    def merge_pdfs(self):
        """
        This is connected to the MERGE_MergeButton, this function will merge the pdf files in the self.pdf_files
        in order.
        """

        file_name = QFileDialog.getSaveFileName(self.parent, 'Save File', 'C:', "pdf files (*.pdf)")
        if file_name[0] is not "":
            output = PyPDF2.PdfFileWriter()
            for pdf_file in self.pdf_files:
                new_reader = PyPDF2.PdfFileReader(pdf_file)
                for page_index in range(new_reader.getNumPages()):
                    output.addPage(new_reader.getPage(page_index))
            with open(file_name[0], 'wb') as outputStream:
                output.write(outputStream)


    def move_up(self):
        """
            This is connected to the clicked event on the buttons to move the pdf files around
        """
        sender = self.parent.sender()
        index = self.up_button_list.index(sender)
        if index != 0:
            self.swap(index, index - 1)

    def move_down(self):
        """
        This is connected to the clicked event on the buttons to move the pdf files around
        """
        sender = self.parent.sender()
        index = self.down_button_list.index(sender)
        if index != len(self.down_button_list) - 1:
            self.swap(index, index + 1)

    def swap(self, index1, index2):
        """
        Used to swap two QFrames in the MERGE_PDFsVLayout based on the two indexes provided.
        This will also change the indexes of the associated pdf files in the self.pdf_files
        """

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