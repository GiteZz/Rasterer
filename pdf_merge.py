from tab_base_class import TabBaseClass
from PyQt5.QtWidgets import QPushButton, QSpinBox, QHBoxLayout, QLabel
from PyQt5.QtWidgets import QGraphicsScene, QFileDialog
from PyQt5.QtGui import QImage, QPixmap, QColor, QPen, QBrush, QPainter, QIcon
import PyQt5.QtCore
from pathlib import Path
import PyPDF2
import pdf2image
from PIL import ImageQt, Image
import os

class PDFMerge(TabBaseClass):
    def __init__(self, parent):
        self.parent = parent

    def confirmUI(self, widgets):
        pass


    def tab_changed(self):
        pass