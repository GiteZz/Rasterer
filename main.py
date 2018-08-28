import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QColor, QPainter, QPen, QTransform, QBrush, QIcon
from PyQt5.QtCore import QPoint, QRect, QPointF, QRectF, QLineF, QSize
from PyQt5.QtWidgets import QGraphicsScene, QFileDialog
from PyQt5.QtPrintSupport import QPrinter
import xml.etree.ElementTree
from ui import Ui_MainWindow
import math
import logging
from graphics_classes import graphicsCrop, graphicsPDF
import os

image_location = "C:/Users/Gilles/Pictures/TestImages/falcon9morning.jpg"


class MyUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.lock_crop_TB = False
        self.lock_crop_LR = False

        self.image_location = None

        self.graphics = QGraphicsScene()
        self.graphics_pixmap = None
        self.image_width = None
        self.image_height = None

        self.graphic_tabs = []

        self.logger = logging.getLogger('main')
        self.logger.info("logger started")
        self.logger.error("hello")

    def confirmUI(self, ui_widgets):
        print("confirming ui")
        self.widgets = ui_widgets
        self.widgets.spinBoxCropTop.valueChanged.connect(self.changeCropTop)
        self.widgets.spinBoxCropBottom.valueChanged.connect(self.changeCropBottom)
        self.widgets.spinBoxCropLeft.valueChanged.connect(self.changeCropLeft)
        self.widgets.spinBoxCropRight.valueChanged.connect(self.changeCropRight)

        self.widgets.cropLeftType.currentIndexChanged.connect(self.changeCropLeft)
        self.widgets.cropRightType.currentIndexChanged.connect(self.changeCropRight)
        self.widgets.cropTopType.currentIndexChanged.connect(self.changeCropTop)
        self.widgets.cropBottomType.currentIndexChanged.connect(self.changeCropBottom)

        ui.pushButtonChooseImage.clicked.connect(self.new_file)

        self.widgets.centralWidget.layout().setContentsMargins(0,0,0,0)

        ui.checkBoxLockLR.stateChanged.connect(self.lockCheckBoxChanged)
        ui.checkBoxLockTB.stateChanged.connect(self.lockCheckBoxChanged)

        ui.pushButtonCreatePDF.clicked.connect(self.pdf_button)

        self.widgets.graphicsViewFullImage.setScene(self.graphics)

        self.graphic_tabs.append(graphicsCrop(self.widgets.graphicsViewFullImage))
        self.graphic_tabs.append(graphicsPDF(self.widgets.graphicsViewPDFImage))
        self.pdf_values_change()

        self.widgets.tabWidget.currentChanged.connect(self.tab_changed)

        self.widgets.spinBoxDesiredSize.valueChanged.connect(self.pdf_values_change)
        self.widgets.spinBoxPDFMarginX.valueChanged.connect(self.pdf_values_change)
        self.widgets.spinBoxPDFMarginY.valueChanged.connect(self.pdf_values_change)
        self.widgets.comboBoxPageRotation.currentIndexChanged.connect(self.pdf_values_change)
        self.widgets.comboBoxDesiredAxis.currentIndexChanged.connect(self.pdf_values_change)

    def new_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file',
                                            'c:\\', "Image files (*.jpg *.png *svg)")
        if fname[0] != "":
            self.set_image(fname[0])

    def pdf_button(self):
        """ Create the rasterized pdf """

        printer = QPrinter(mode=QPrinter.HighResolution)
        printer.setOutputFileName("hello.pdf")
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setFullPage(True)
        printer.setPaperSize(QPrinter.A4)

        painter = QPainter()
        painter.begin(printer)

        pdf_x_px = printer.width()
        pdf_y_px = printer.height()

        pdf_values = self.getPDF_values(pdf_x_px, pdf_y_px)

        createPDF(self.widgets.comboBoxMarking.currentText(), *pdf_values, printer, painter)

        painter.end()

    def tab_changed(self):
        print("tab changed")
        for tab in self.graphic_tabs:
            tab.update()

    def lockCheckBoxChanged(self):
        self.lock_crop_TB = ui.checkBoxLockTB.isChecked()
        self.lock_crop_LR = ui.checkBoxLockLR.isChecked()

    def changeCropLeft(self):
        """ event when self.widgets.spinBoxCropLeft changes value, individual events in order the enable locking"""
        if self.lock_crop_LR:
            self.widgets.spinBoxCropRight.setValue(self.widgets.spinBoxCropLeft.value())
            self.widgets.cropRightType.setCurrentIndex(self.widgets.cropLeftType.currentIndex())

        self.changeCrop()

    def changeCropRight(self):
        """ event when self.widgets.spinBoxCropRight changes value, individual events in order the enable locking"""
        if self.lock_crop_LR:
            self.widgets.spinBoxCropLeft.setValue(self.widgets.spinBoxCropRight.value())
            self.widgets.cropLeftType.setCurrentIndex(self.widgets.cropRightType.currentIndex())
        self.changeCrop()

    def changeCropTop(self):
        """ event when self.widgets.spinBoxCropTop changes value, individual events in order the enable locking"""
        if self.lock_crop_TB:
            self.widgets.spinBoxCropBottom.setValue(self.widgets.spinBoxCropTop.value())
            self.widgets.cropBottomType.setCurrentIndex(self.widgets.cropTopType.currentIndex())
        self.changeCrop()

    def changeCropBottom(self):
        """ event when self.widgets.spinBoxCropBottom changes value, individual events in order the enable locking"""
        if self.lock_crop_TB:
            self.widgets.spinBoxCropTop.setValue(self.widgets.spinBoxCropBottom.value())
            self.widgets.cropTopType.setCurrentIndex(self.widgets.cropBottomType.currentIndex())
        self.changeCrop()

    def get_crop_value_left(self):
        image_size = self.graphic_tabs[0].original_pix.size()

        if self.widgets.cropLeftType.currentText() == "px":
            crop_left_px = self.widgets.spinBoxCropLeft.value()
        else:
            crop_left_px = int(self.widgets.spinBoxCropLeft.value() * 0.01 * image_size.width())

        return crop_left_px

    def get_crop_value_right(self):
        image_size = self.graphic_tabs[0].original_pix.size()

        if self.widgets.cropRightType.currentText() == "px":
            crop_right_px = self.widgets.spinBoxCropRight.value()
        else:
            crop_right_px = int(self.widgets.spinBoxCropRight.value() * 0.01 * image_size.width())

        return crop_right_px

    def get_crop_value_top(self):
        image_size = self.graphic_tabs[0].original_pix.size()

        if self.widgets.cropTopType.currentText() == "px":
            crop_top_px = self.widgets.spinBoxCropTop.value()
        else:
            crop_top_px = int(self.widgets.spinBoxCropTop.value() * 0.01 * image_size.height())

        return crop_top_px

    def get_crop_value_bottom(self):
        image_size = self.graphic_tabs[0].original_pix.size()

        if self.widgets.cropBottomType.currentText() == "px":
            crop_bottom_px = self.widgets.spinBoxCropBottom.value()
        else:
            crop_bottom_px = int(self.widgets.spinBoxCropBottom.value() * 0.01 * image_size.height())

        return crop_bottom_px

    def get_crop_values(self, scale_factor_x=1, scale_factor_y=1):
        """ gives crop values in px based op current_pixmap"""

        ret_left = int(scale_factor_x * self.get_crop_value_left())
        ret_right = int(scale_factor_x * self.get_crop_value_right())

        ret_top = int(scale_factor_y * self.get_crop_value_top())
        ret_bottom = int(scale_factor_y * self.get_crop_value_bottom())

        return ret_left, ret_right, ret_top, ret_bottom

    def changeCrop(self):
        print("crop changed")
        crop_values = self.get_crop_values()
        for tab in self.graphic_tabs:
            tab.change_crop(*crop_values)

    def pdf_values_change(self):
        # pdate_pdf_values(self, des_size_mm, width, margin_x_mm, margin_y_mm, A4_vertical)
        des_size_mm = self.widgets.spinBoxDesiredSize.value()
        width = self.widgets.comboBoxDesiredAxis.currentText() == "wide"
        margin_x_mm = self.widgets.spinBoxPDFMarginX.value()
        margin_y_mm = self.widgets.spinBoxPDFMarginY.value()
        A4_vertical = self.widgets.comboBoxPageRotation.currentText() == "vertical"

        self.graphic_tabs[1].set_pdf_values(des_size_mm, width, margin_x_mm, margin_y_mm, A4_vertical)
        print("pdf values changed")

    def resizeEvent(self, *args, **kwargs):
        super().resizeEvent(*args, **kwargs)
        print("resize event")
        self.handle_resizing()

    def handle_resizing(self):
        for tab in self.graphic_tabs:
            tab.update()

    def set_image(self, location):
        print("setting image from: ", location)
        self.image_location = location
        for tab in self.graphic_tabs:
            tab.set_image(location)


        # TODO set maximum for spinboxes

    def get_cropped_image(self):
        filename, file_extension = os.path.splitext(self.image_location)
        if file_extension == ".svg":
            e = xml.etree.ElementTree.parse(self.image_location).getroot()
            width = int(e.get('width'))
            height = int(e.get('height'))
            des_width = 10000
            des_mul = math.ceil(des_width / width)
            size = QSize(des_mul * width, des_mul * height)
            image_non_cropped = QIcon(self.image_location).pixmap(size).toImage()
            #original is displayed with 2000 width for speed
            scale_factor = 5
        else:
            image_non_cropped = QImage(self.image_location)
            scale_factor = 1

        im_size = image_non_cropped.size()
        crop_left_px, crop_right_px, crop_top_px, crop_bottom_px = self.get_crop_values(scale_factor_x=scale_factor, scale_factor_y=scale_factor)

        crop_top_left = QPoint(crop_left_px, crop_top_px)
        crop_bottom_right = QPoint(im_size.width() - crop_right_px, im_size.height() - crop_bottom_px)

        image_cropped = image_non_cropped.copy(QRect(crop_top_left, crop_bottom_right))

        return image_cropped

    def getPDF_values(self, pdf_x_px, pdf_y_px):
        image_cropped = self.get_cropped_image()

        margin_x_mm = self.widgets.spinBoxPDFMarginX.value()
        margin_y_mm = self.widgets.spinBoxPDFMarginY.value()
        desired_mm = self.widgets.spinBoxDesiredSize.value()
        desired_direction = self.widgets.comboBoxDesiredAxis.currentText()
        page_rotation = self.widgets.comboBoxPageRotation.currentText()

        A4_width = 210  # mm
        A4_height = 297  # mm

        # instead of using a different function, just rotate the image and change the desired direction
        if page_rotation == "horizontal":
            transform = QTransform()
            transform.rotate(90)
            image_cropped = image_cropped.transformed(transform)
            if desired_direction == "wide":
                desired_direction = "heigh"
            else:
                desired_direction = "wide"

        im_size = image_cropped.size()
        im_width = im_size.width()
        im_height = im_size.height()
        im_ratio = im_width / im_height

        if desired_direction == "wide":
            des_x_mm = desired_mm
            des_y_mm = des_x_mm * (1 / im_ratio)
        else:
            des_y_mm = desired_mm
            des_x_mm = des_y_mm * im_ratio

        # available pixels in x and y direction
        av_x_mm = A4_width - 2 * margin_x_mm
        av_y_mm = A4_height - 2 * margin_y_mm

        av_x_px = (av_x_mm / A4_width) * pdf_x_px
        av_y_px = (av_y_mm / A4_height) * pdf_y_px

        amount_x = des_x_mm / av_x_mm
        amount_y = des_y_mm / av_y_mm

        return image_cropped, amount_x, amount_y, av_x_px, av_y_px

def drawHalfCross(point_TL, point_BR, margin_x_px, margin_y_px, max_x, max_y, painter):
    pen = QPen(QColor(0,0,0))
    pen.setWidth(5)
    painter.setPen(pen)

    # top left
    painter.drawLine(point_TL.x() - margin_x_px, point_TL.y(), point_TL.x(), point_TL.y())
    painter.drawLine(point_TL.x(), point_TL.y() - margin_y_px, point_TL.x(), point_TL.y())

    # top right
    painter.drawLine(point_BR.x() + margin_x_px, point_TL.y(), point_BR.x(), point_TL.y())
    painter.drawLine(point_BR.x(), point_TL.y() - margin_y_px, point_BR.x(), point_TL.y())

    # bottom left
    painter.drawLine(point_TL.x() - margin_x_px, point_BR.y(), point_TL.x(), point_BR.y())
    painter.drawLine(point_TL.x(), point_BR.y() + margin_y_px, point_TL.x(), point_BR.y())

    # bottom right
    painter.drawLine(point_BR.x() + margin_x_px, point_BR.y(), point_BR.x(), point_BR.y())
    painter.drawLine(point_BR.x(), point_BR.y() + margin_y_px, point_BR.x(), point_BR.y())

def drawFullCross(point_TL, point_BR, margin_x_px, margin_y_px, max_x, max_y, painter):
    pen = QPen(QColor(0,0,0))
    pen.setWidth(5)
    painter.setPen(pen)

    # top left
    painter.drawLine(point_TL.x() - margin_x_px, point_TL.y(), point_TL.x() + margin_x_px, point_TL.y())
    painter.drawLine(point_TL.x(), point_TL.y() - margin_y_px, point_TL.x(), point_TL.y() + margin_y_px)

    # top right
    painter.drawLine(point_BR.x() - margin_x_px, point_TL.y(), point_BR.x() + margin_x_px, point_TL.y())
    painter.drawLine(point_BR.x(), point_TL.y() - margin_y_px, point_BR.x(), point_TL.y() + margin_y_px)

    # bottom left
    painter.drawLine(point_TL.x() - margin_x_px, point_BR.y(), point_TL.x() + margin_x_px, point_BR.y())
    painter.drawLine(point_TL.x(), point_BR.y() - margin_y_px, point_TL.x(), point_BR.y() + margin_y_px)

    # bottom right
    painter.drawLine(point_BR.x() - margin_x_px, point_BR.y(), point_BR.x() + margin_x_px, point_BR.y())
    painter.drawLine(point_BR.x(), point_BR.y() - margin_y_px, point_BR.x(), point_BR.y() + margin_y_px)

def drawFullLine(point_TL, point_BR, margin_x_px, margin_y_px, max_x, max_y, painter):
    pen = QPen(QColor(0,0,0))
    pen.setWidth(5)
    painter.setPen(pen)

    # left
    painter.drawLine(point_TL.x(), 0, point_TL.x(), max_y)

    # top
    painter.drawLine(0, point_TL.y(), max_x, point_TL.y())

    # right
    painter.drawLine(point_BR.x(), 0, point_BR.x(), max_y)

    # bottom
    painter.drawLine(0, point_BR.y(), max_x, point_BR.y())

def drawNothing(point_TL, point_BR, margin_x_px, margin_y_px, max_x, max_y, painter):
    pass

def createPDF(marking, image, amount_x, amount_y, av_x_px, av_y_px, printer, painter):
    """ Divides image over multiple pdf pages according to the parameters """
    pdf_x_px = printer.width()
    pdf_y_px = printer.height()

    image_size = image.size()
    im_x_px = image_size.width()
    im_y_px = image_size.height()

    mark_function = drawNothing

    if marking == "Full cross":
        mark_function = drawFullCross
    if marking == "Half cross":
        mark_function = drawHalfCross
    if marking == "Full line":
        mark_function = drawFullLine

    amount_whole_x = math.floor(amount_x)
    amount_whole_y = math.floor(amount_y)

    seg_im_x_px = im_x_px / amount_x
    seg_im_y_px = im_y_px / amount_y

    im_rest_x_px = im_x_px - amount_whole_x * seg_im_x_px
    im_rest_y_px = im_y_px - amount_whole_y * seg_im_y_px

    pdf_rest_x_px = (amount_x - amount_whole_x) * pdf_x_px
    pdf_rest_y_px = (amount_y - amount_whole_y) * pdf_y_px

    margin_x_px = (pdf_x_px - av_x_px) / 2
    margin_y_px = (pdf_y_px - av_y_px) / 2

    # print the parts of the image that take up a whole page
    for x in range(amount_whole_x):
        for y in range(amount_whole_y):
            target_top_left = QPoint(margin_x_px, margin_y_px)
            target_bottom_right = QPoint(margin_x_px + av_x_px, margin_y_px + av_y_px)

            source_top_left = QPoint(x * seg_im_x_px, y * seg_im_y_px)
            source_bottom_right = QPoint((x + 1) * seg_im_x_px, (y + 1) * seg_im_y_px)

            rect_target = QRect(target_top_left, target_bottom_right)
            rect_source = QRect(source_top_left, source_bottom_right)

            painter.drawImage(rect_target, image, rect_source)

            mark_function(target_top_left, target_bottom_right, margin_x_px, margin_y_px, pdf_x_px, pdf_y_px, painter)

            printer.newPage()

    # print the partial pages in the y direction
    if im_rest_y_px != 0:
        for x in range(amount_whole_x):
            target_top_left = QPoint(margin_x_px, margin_y_px)
            target_bottom_right = QPoint(margin_x_px + av_x_px, margin_y_px + pdf_rest_y_px)

            source_top_left = QPoint(x * seg_im_x_px, amount_whole_y * seg_im_y_px)
            source_bottom_right = QPoint((x + 1) * seg_im_x_px, amount_whole_y * seg_im_y_px + im_rest_y_px)

            rect_target = QRect(target_top_left, target_bottom_right)
            rect_source = QRect(source_top_left, source_bottom_right)

            painter.drawImage(rect_target, image, rect_source)

            mark_function(target_top_left, target_bottom_right, margin_x_px, margin_y_px, pdf_x_px, pdf_y_px, painter)

            printer.newPage()

    # print the partial pages in the x direction
    if im_rest_x_px != 0:
        for y in range(amount_whole_y):
            target_top_left = QPoint(margin_x_px, margin_y_px)
            target_bottom_right = QPoint(margin_x_px + pdf_rest_x_px, margin_y_px + av_y_px)

            source_top_left = QPoint(amount_whole_x * seg_im_x_px, y * seg_im_y_px)
            source_bottom_right = QPoint(amount_whole_x * seg_im_x_px + im_rest_x_px, (y + 1) * seg_im_y_px)

            rect_target = QRect(target_top_left, target_bottom_right)
            rect_source = QRect(source_top_left, source_bottom_right)

            painter.drawImage(rect_target, image, rect_source)

            mark_function(target_top_left, target_bottom_right, margin_x_px, margin_y_px, pdf_x_px, pdf_y_px, painter)

            printer.newPage()

    # print the corner consisting of both partial pages
    if im_rest_x_px != 0 and im_rest_y_px != 0:
        target_top_left = QPoint(margin_x_px, margin_y_px)
        target_bottom_right = QPoint(margin_x_px + pdf_rest_x_px, margin_y_px + pdf_rest_y_px)

        source_top_left = QPoint((amount_whole_x + 1) * seg_im_x_px, (amount_whole_y + 1) * seg_im_y_px)
        source_bottom_right = QPoint((amount_whole_x + 1) * seg_im_x_px + im_rest_x_px,
                                     (amount_whole_y + 1) * seg_im_y_px + im_rest_y_px)

        rect_target = QRect(target_top_left, target_bottom_right)
        rect_source = QRect(source_top_left, source_bottom_right)

        painter.drawImage(rect_target, image, rect_source)

        mark_function(target_top_left, target_bottom_right, margin_x_px, margin_y_px, pdf_x_px, pdf_y_px, painter)

    print("pdf created")


if __name__ == "__main__":
    monitor_width = 1920
    monitor_height = 1080

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MyUI()
    ui = Ui_MainWindow()

    ui.setupUi(MainWindow)
    MainWindow.confirmUI(ui)
    #MainWindow.set_image(image_location)
    MainWindow.set_image("C:/Users/Gilles/Documents/svg_exporter.svg")

    MainWindow.show()
    MainWindow.handle_resizing()
    sys.exit(app.exec_())