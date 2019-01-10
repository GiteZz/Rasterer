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

        self.from_spinboxes = [self.widgets.SPLIT_FirstFromSpinbox]
        self.to_spinboxes = [self.widgets.SPLIT_FirstToSpinbox]
        self.range_to_labels = [self.widgets.SPLIT_FirstFromLabel]
        self.range_from_labels = [self.widgets.SPLIT_FirstToLabel]
        self.range_buttons = [self.widgets.SPLIT_FirstDeleteRangeButton]
        self.range_Hlayouts = [self.widgets.SPLIT_FirstRangeHLayout]
        self.widgets.SPLIT_FirstDeleteRangeButton.setFixedSize(self.remove_range_size)

        self.from_spinboxes[0].valueChanged.connect(self.page_spinbox_changed)
        self.to_spinboxes[0].valueChanged.connect(self.page_spinbox_changed)
        self.range_buttons[0].clicked.connect(self.delete_range)

        self.widgets.SPLIT_AddRangeButton.clicked.connect(self.new_range)

        self.widgets.SPLIT_LoadpdfButton.clicked.connect(self.load_new_pdf)

        self.widgets.SPLIT_FirstPageView.setScene(self.first_page_scene)
        self.widgets.SPLIT_LastPageView.setScene(self.last_page_scene)

        self.pages_pixmap = [None, None]
        self.pages_scaled_pixmap = [None, None]
        self.pages_scene_pixmap = [None, None]
        self.pages_images = [None, None]
        self.pages_scenes = [self.first_page_scene, self.last_page_scene]
        self.graphic_views = [self.widgets.SPLIT_FirstPageView, self.widgets.SPLIT_LastPageView]

        self.widgets.SPLIT_CreateButton.clicked.connect(self.split_pdf)

        self.widgets.SPLIT_FirstPageView.setHorizontalScrollBarPolicy(1)
        self.widgets.SPLIT_FirstPageView.setVerticalScrollBarPolicy(1)
        self.widgets.SPLIT_LastPageView.setHorizontalScrollBarPolicy(1)
        self.widgets.SPLIT_LastPageView.setVerticalScrollBarPolicy(1)

        self.amount_pages = None

        self.set_new_pdf('c:/Users/Gilles/Downloads/TheorieVragenDB.pdf')

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
        self.pdf_path, self.pdf_name = os.path.split(pdf_name)

        self.pdf_read = PyPDF2.PdfFileReader(pdf_name)
        self.amount_pages = self.pdf_read.getNumPages()

        for i in range(len(self.range_Hlayouts)):
            self.from_spinboxes[i].setMaximum(self.amount_pages)
            self.to_spinboxes[i].setMaximum(self.amount_pages)

        if len(self.range_Hlayouts) > 0:
            self.to_spinboxes[0].setValue(self.amount_pages)
            self.set_pdf_pages(0)


    def get_range(self, index):
        from_range = self.from_spinboxes[index].value()
        to_range = self.to_spinboxes[index].value()

        return from_range, to_range

    def set_pdf_pages(self, range_index):
        pass
        if self.pdf_path is None:
            pass

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
        for i in range(2):
            if self.pages_pixmap[i] is not None:
                scene_size = self.graphic_views[i].size()
                self.pages_scaled_pixmap[i] = self.pages_pixmap[i].scaled(scene_size, aspectRatioMode=1)
                self.pages_scene_pixmap[i] = self.pages_scenes[i].addPixmap(self.pages_scaled_pixmap[i])

    def split_pdf(self):
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
        sender = self.parent.sender()
        if sender in self.from_spinboxes:
            index = self.from_spinboxes.index(sender)
        else:
            index = self.to_spinboxes.index(sender)
        self.set_pdf_pages(index)
        print(f'spinbox changed to new value {new_value}')

    def new_range(self):
        self.range_Hlayouts.append(QHBoxLayout())
        self.from_spinboxes.append(QSpinBox())
        self.to_spinboxes.append(QSpinBox())
        self.range_from_labels.append(QLabel('from: '))
        self.range_to_labels.append(QLabel('to: '))
        self.range_buttons.append(QPushButton('-'))

        self.range_Hlayouts[-1].addWidget(self.range_from_labels[-1])
        self.range_Hlayouts[-1].addWidget(self.from_spinboxes[-1])
        self.range_Hlayouts[-1].addWidget(self.range_to_labels[-1])
        self.range_Hlayouts[-1].addWidget(self.to_spinboxes[-1])
        self.range_Hlayouts[-1].addWidget(self.range_buttons[-1])

        self.from_spinboxes[-1].setMinimum(1)
        self.to_spinboxes[-1].setMinimum(1)

        self.range_buttons[-1].setFixedSize(self.remove_range_size)

        if self.amount_pages is None:
            self.from_spinboxes[-1].setMaximum(1)
            self.to_spinboxes[-1].setMaximum(1)
        else:
            self.from_spinboxes[-1].setMaximum(self.amount_pages)
            self.to_spinboxes[-1].setMaximum(self.amount_pages)


        self.range_buttons[-1].clicked.connect(self.delete_range)
        self.from_spinboxes[-1].valueChanged.connect(self.page_spinbox_changed)
        self.to_spinboxes[-1].valueChanged.connect(self.page_spinbox_changed)

        self.widgets.SPLIT_SplitsVLayout.addLayout(self.range_Hlayouts[-1])
        print('new range')
        pass

    def delete_range(self):
        button = self.parent.sender()
        i = self.range_buttons.index(button)
        print(i)

        self.from_spinboxes.pop(i).deleteLater()
        self.to_spinboxes.pop(i).deleteLater()
        self.range_buttons.pop(i).deleteLater()
        self.range_Hlayouts.pop(i).deleteLater()
        self.range_to_labels.pop(i).deleteLater()
        self.range_from_labels.pop(i).deleteLater()

        print(i)
