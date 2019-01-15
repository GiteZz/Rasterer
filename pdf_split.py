from tab_base_class import TabBaseClass
from PyQt5.QtWidgets import QPushButton, QSpinBox, QHBoxLayout, QLabel
from PyQt5.QtWidgets import QGraphicsScene, QFileDialog
from PyQt5.QtGui import QImage, QPixmap, QColor, QPen, QBrush, QPainter, QIcon
from PyQt5.QtCore import QPoint, QRect, QSize
import PyQt5.QtCore
from pathlib import Path
import PyPDF2
import pdf2image
from PIL import ImageQt, Image
import os


class PDFSplit(TabBaseClass):
    def __init__(self, parent):
        self.parent = parent

        self.first_page_scene = QGraphicsScene()
        self.last_page_scene = QGraphicsScene()

        self.remove_range_size = QSize(25, 25)

        self.current_viewing_pages = [None, None]

    def confirmUI(self, widgets):
        self.widgets = widgets
        # Create the lists to easily find the indexes of the UI elements
        self.from_spinboxes = [self.widgets.SPLIT_FirstFromSpinbox]
        self.to_spinboxes = [self.widgets.SPLIT_FirstToSpinbox]
        self.range_to_labels = [self.widgets.SPLIT_FirstFromLabel]
        self.range_from_labels = [self.widgets.SPLIT_FirstToLabel]
        self.range_delete_buttons = [self.widgets.SPLIT_FirstDeleteRangeButton]
        self.range_Hlayouts = [self.widgets.SPLIT_FirstRangeHLayout]

        # Make the button square
        self.widgets.SPLIT_FirstDeleteRangeButton.setFixedSize(self.remove_range_size)

        # Add the functions to reacted to changed spinboxes and delete buttons
        self.from_spinboxes[0].valueChanged.connect(self.page_spinbox_changed)
        self.to_spinboxes[0].valueChanged.connect(self.page_spinbox_changed)
        self.range_delete_buttons[0].clicked.connect(self.delete_range)

        self.widgets.SPLIT_AddRangeButton.clicked.connect(self.new_range)
        self.widgets.SPLIT_LoadpdfButton.clicked.connect(self.load_new_pdf)
        self.widgets.SPLIT_CreateButton.clicked.connect(self.split_pdf)

        self.widgets.SPLIT_FirstPageView.setScene(self.first_page_scene)
        self.widgets.SPLIT_LastPageView.setScene(self.last_page_scene)

        # These list are created to make updating them easier
        self.pages_pixmap = [None, None]
        self.pages_scaled_pixmap = [None, None]
        self.pages_scene_pixmap = [None, None]
        self.pages_images = [None, None]
        self.pages_scenes = [self.first_page_scene, self.last_page_scene]
        self.graphic_views = [self.widgets.SPLIT_FirstPageView, self.widgets.SPLIT_LastPageView]

        # Disallow scrollbars on the graphicsviews
        self.widgets.SPLIT_FirstPageView.setHorizontalScrollBarPolicy(1)
        self.widgets.SPLIT_FirstPageView.setVerticalScrollBarPolicy(1)
        self.widgets.SPLIT_LastPageView.setHorizontalScrollBarPolicy(1)
        self.widgets.SPLIT_LastPageView.setVerticalScrollBarPolicy(1)

        self.amount_pages = None

    def tab_changed(self):
        pass

    def handle_resizing(self):
        self.scale_pages()


    def load_new_pdf(self):
        fname = QFileDialog.getOpenFileName(self.parent, 'Open file',
                                            'c:/Users/Gilles/Downloads', "pdf files (*.pdf)")
        if fname[0] != "":
            self.set_new_pdf(fname[0])

    def set_new_pdf(self, pdf_name):
        """
        Replace the current PDF file and adjust the max and min from the UI
        :param pdf_name: The new pdf file in the form path/filename.pdf
        :return:
        """
        self.pdf_path, self.pdf_name = os.path.split(pdf_name)

        self.pdf_read = PyPDF2.PdfFileReader(pdf_name)
        self.amount_pages = self.pdf_read.getNumPages()

        for i in range(len(self.range_Hlayouts)):
            self.from_spinboxes[i].setMaximum(self.amount_pages)
            self.to_spinboxes[i].setMaximum(self.amount_pages)

        if len(self.range_Hlayouts) > 0:
            self.to_spinboxes[0].setValue(self.amount_pages)
            self.set_pdf_pages(0)


    def get_range(self, range_index):
        """
        Creates the tupe with the start and end page of that range
        :param range_index: The index of the range
        :return: The tuple (from_page, to_page) as pagenumbers
        """
        from_range = self.from_spinboxes[range_index].value()
        to_range = self.to_spinboxes[range_index].value()

        return from_range, to_range

    def set_pdf_pages(self, range_index):
        """
        This function is used to show the current pdf pages in the graphicsviews.
        The current pdf pages are based on the range index.
        :param range_index:
        :return:
        """
        if self.pdf_path is None:
            return

        pdf_range = self.get_range(range_index)

        for i in range(2):
            if pdf_range[i] != self.current_viewing_pages[i]:
                im = pdf2image.convert_from_path(f'{self.pdf_path}/{self.pdf_name}', first_page=pdf_range[i],
                                                 last_page=pdf_range[i], dpi=100)[0].convert('RGB')

                self.pages_images[i] = ImageQt.ImageQt(im)
                self.pages_pixmap[i] = QPixmap.fromImage(self.pages_images[i])

        self.current_viewing_pages = pdf_range

        self.scale_pages()

    def scale_pages(self):
        """
        Used to adjust the pixmap size when scaling occurs, or a new pixmaps are created
        :return: Nothing
        """
        for i in range(2):
            if self.pages_pixmap[i] is not None:
                scene_size = self.graphic_views[i].size()
                self.pages_scaled_pixmap[i] = self.pages_pixmap[i].scaled(scene_size, aspectRatioMode=1)
                self.pages_scene_pixmap[i] = self.pages_scenes[i].addPixmap(self.pages_scaled_pixmap[i])

    def split_pdf(self):
        """
        Connnected to the SPLIT_CreateButton button, splits the PDF in pieces and saves them.
        Gets saved with original path and name appended with to and from index.
        :return: Nothing
        """
        from_list = []
        to_list = []

        for spinbox in self.from_spinboxes:
            from_list.append(spinbox.value())

        for spinbox in self.to_spinboxes:
            to_list.append(spinbox.value())

        new_path = self.pdf_path

        for from_index, to_index in zip(from_list, to_list):
            output = PyPDF2.PdfFileWriter()
            for i in range(from_index, to_index + 1):
                output.addPage(self.pdf_read.getPage(i - 1))

            with open(f'{new_path}/{self.pdf_name[:-4]}_{from_index}-{to_index}.pdf', "wb") as outputStream:
                output.write(outputStream)

    def page_spinbox_changed(self, new_value):
        """
        This function is connected to all the from and to_spinboxes.
        It finds the index of the range and then calls a function to update the graphicsviews
        :param new_value: new values of spinbox, not used
        :return: Nothing
        """
        sender = self.parent.sender()
        if sender in self.from_spinboxes:
            index = self.from_spinboxes.index(sender)
        else:
            index = self.to_spinboxes.index(sender)
        self.set_pdf_pages(index)

    def new_range(self):
        """
        This function is connected to the SPLIT_AddRange button and creates the UI to support a new range
        :return: Nothing
        """
        self.range_Hlayouts.append(QHBoxLayout())
        self.from_spinboxes.append(QSpinBox())
        self.to_spinboxes.append(QSpinBox())
        self.range_from_labels.append(QLabel('from: '))
        self.range_to_labels.append(QLabel('to: '))
        self.range_delete_buttons.append(QPushButton('-'))

        self.range_Hlayouts[-1].addWidget(self.range_from_labels[-1])
        self.range_Hlayouts[-1].addWidget(self.from_spinboxes[-1])
        self.range_Hlayouts[-1].addWidget(self.range_to_labels[-1])
        self.range_Hlayouts[-1].addWidget(self.to_spinboxes[-1])
        self.range_Hlayouts[-1].addWidget(self.range_delete_buttons[-1])

        self.from_spinboxes[-1].setMinimum(1)
        self.to_spinboxes[-1].setMinimum(1)

        self.range_delete_buttons[-1].setFixedSize(self.remove_range_size)

        if self.amount_pages is None:
            self.from_spinboxes[-1].setMaximum(1)
            self.to_spinboxes[-1].setMaximum(1)
        else:
            self.from_spinboxes[-1].setMaximum(self.amount_pages)
            self.to_spinboxes[-1].setMaximum(self.amount_pages)


        self.range_delete_buttons[-1].clicked.connect(self.delete_range)
        self.from_spinboxes[-1].valueChanged.connect(self.page_spinbox_changed)
        self.to_spinboxes[-1].valueChanged.connect(self.page_spinbox_changed)

        self.widgets.SPLIT_SplitsVLayout.addLayout(self.range_Hlayouts[-1])
        print('new range')
        pass

    def delete_range(self):
        """
        Connected to the buttons in the self.range_delete_buttons, remove the UI for that specific range
        :return: Nothing
        """
        button = self.parent.sender()
        i = self.range_delete_buttons.index(button)

        self.from_spinboxes.pop(i).deleteLater()
        self.to_spinboxes.pop(i).deleteLater()
        self.range_delete_buttons.pop(i).deleteLater()
        self.range_Hlayouts.pop(i).deleteLater()
        self.range_to_labels.pop(i).deleteLater()
        self.range_from_labels.pop(i).deleteLater()
