import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QColor, QPainter, QPen, QTransform, QBrush
from PyQt5.QtCore import QPoint, QRect, QPointF, QRectF, QLineF
from PyQt5.QtWidgets import QGraphicsScene, QFileDialog
from PyQt5.QtPrintSupport import QPrinter
from ui import Ui_MainWindow
import math
import logging

image_location = "C:/Users/Gilles/Pictures/TestImages/falcon9morning.jpg"


class MyUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.lock_crop_TB = False
        self.lock_crop_LR = False

        self.image_location = None

        self.graphics = QGraphicsScene()
        self.graphics_pixmap = None
        self.current_pixmap = None
        self.image_width = None
        self.image_height = None

        self.graphics_crop_rect_bottom = None
        self.graphics_crop_rect_top = None
        self.graphics_crop_rect_left = None
        self.graphics_crop_rect_right = None

        self.graphics_crop_line_full_bottom = None
        self.graphics_crop_line_full_top = None
        self.graphics_crop_line_full_left = None
        self.graphics_crop_line_full_right = None

        self.graphics_crop_line_dot_bottom = None
        self.graphics_crop_line_dot_top = None
        self.graphics_crop_line_dot_left = None
        self.graphics_crop_line_dot_right = None

        self.logger = logging.getLogger('main')
        self.logger.info("logger started")
        self.logger.error("hello")

    def confirmUI(self, ui_widgets):
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

        #ui.menuOpen_File.aboutToShow.connect(self.new_file)

        ui.checkBoxLockLR.stateChanged.connect(self.lockCheckBoxChanged)
        ui.checkBoxLockTB.stateChanged.connect(self.lockCheckBoxChanged)

        ui.pushButtonCreatePDF.clicked.connect(self.pdf_button)

        self.widgets.graphicsView.setScene(self.graphics)

        # disable scroll bars
        self.widgets.graphicsView.setHorizontalScrollBarPolicy(1)
        self.widgets.graphicsView.setVerticalScrollBarPolicy(1)

        # used to create dummy rectangles
        TL = QPoint(0, 0)
        BR = QPoint(0, 0)

        # draw the rectangles in a see through black
        brush = QBrush(QColor(0, 0, 0, 50))

        # create pen that draws nothing, used for rectangles without border
        empty_pen = QPen(QColor(0,0,0,255))
        empty_pen.setStyle(0)

        # these two together create a white/black dotted line
        full_pen = QPen(QColor(255,255,255))
        dot_pen = QPen(QColor(0,0,0))
        dot_pen.setStyle(3)

        self.graphics_crop_rect_bottom = self.graphics.addRect(QRectF(TL, BR), brush= brush, pen= empty_pen)
        self.graphics_crop_rect_top = self.graphics.addRect(QRectF(TL, BR), brush= brush, pen= empty_pen)
        self.graphics_crop_rect_left = self.graphics.addRect(QRectF(TL, BR), brush= brush, pen= empty_pen)
        self.graphics_crop_rect_right = self.graphics.addRect(QRectF(TL, BR), brush= brush, pen= empty_pen)

        self.graphics_crop_line_full_bottom = self.graphics.addLine(QLineF(TL, BR), pen=full_pen)
        self.graphics_crop_line_full_top = self.graphics.addLine(QLineF(TL, BR), pen=full_pen)
        self.graphics_crop_line_full_left = self.graphics.addLine(QLineF(TL, BR), pen=full_pen)
        self.graphics_crop_line_full_right = self.graphics.addLine(QLineF(TL, BR), pen=full_pen)

        self.graphics_crop_line_dot_bottom = self.graphics.addLine(QLineF(TL, BR), pen=dot_pen)
        self.graphics_crop_line_dot_top = self.graphics.addLine(QLineF(TL, BR), pen=dot_pen)
        self.graphics_crop_line_dot_left = self.graphics.addLine(QLineF(TL, BR), pen=dot_pen)
        self.graphics_crop_line_dot_right = self.graphics.addLine(QLineF(TL, BR), pen=dot_pen)

    def new_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file',
                                            'c:\\', "Image files (*.jpg *.png)")
        if fname[0] != "":
            self.set_image(fname[0])

    def pdf_button(self):
        """ Create the rasterized pdf """
        image_non_cropped = QImage(self.image_location)
        im_size = image_non_cropped.size()
        crop_left_pos, crop_right_px, crop_top_pos, crop_bottom_px = self.get_crop_values(relative=False)

        crop_top_left = QPoint(crop_left_pos, crop_top_pos)
        crop_bottom_right = QPoint(im_size.width() - crop_right_px, im_size.height() - crop_bottom_px)

        image_cropped = image_non_cropped.copy(QRect(crop_top_left, crop_bottom_right))

        marking = ["halfCross", "fullCross", "fullLine", "nothing"][self.widgets.comboBoxMarking.currentIndex()]
        createPDF(image_cropped,
                  self.widgets.spinBoxPDFMarginX.value(), self.widgets.spinBoxPDFMarginY.value(),
                  self.widgets.spinBoxDesiredSize.value(), self.widgets.comboBoxDesiredAxis.currentText(),
                  marking, self.widgets.comboBoxPageRotation.currentText(), "new.pdf")

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

    def checkVisibility(self):
        """ Hides lines and rects on the graphicsview if they are not necessary """
        self.graphics_crop_line_full_bottom.setVisible(self.widgets.spinBoxCropBottom.value() != 0)
        self.graphics_crop_line_dot_bottom.setVisible(self.widgets.spinBoxCropBottom.value() != 0)
        self.graphics_crop_rect_bottom.setVisible(self.widgets.spinBoxCropBottom.value() != 0)

        self.graphics_crop_line_full_top.setVisible(self.widgets.spinBoxCropTop.value() != 0)
        self.graphics_crop_line_dot_top.setVisible(self.widgets.spinBoxCropTop.value() != 0)
        self.graphics_crop_rect_top.setVisible(self.widgets.spinBoxCropTop.value() != 0)

        self.graphics_crop_line_full_right.setVisible(self.widgets.spinBoxCropRight.value() != 0)
        self.graphics_crop_line_dot_right.setVisible(self.widgets.spinBoxCropRight.value() != 0)
        self.graphics_crop_rect_right.setVisible(self.widgets.spinBoxCropRight.value() != 0)

        self.graphics_crop_line_full_left.setVisible(self.widgets.spinBoxCropLeft.value() != 0)
        self.graphics_crop_line_dot_left.setVisible(self.widgets.spinBoxCropLeft.value() != 0)
        self.graphics_crop_rect_left.setVisible(self.widgets.spinBoxCropLeft.value() != 0)


    def get_crop_value_left(self):
        image_size = self.current_pixmap.size()

        if self.widgets.cropLeftType.currentText() == "px":
            crop_left_px = self.widgets.spinBoxCropLeft.value()
        else:
            crop_left_px = int(self.widgets.spinBoxCropLeft.value() * 0.01 * image_size.width())

        return crop_left_px

    def get_crop_value_right(self):
        image_size = self.current_pixmap.size()

        if self.widgets.cropRightType.currentText() == "px":
            crop_right_px = self.widgets.spinBoxCropRight.value()
        else:
            crop_right_px = int(self.widgets.spinBoxCropRight.value() * 0.01 * image_size.width())

        return crop_right_px

    def get_crop_value_top(self):
        image_size = self.current_pixmap.size()

        if self.widgets.cropTopType.currentText() == "px":
            crop_top_px = self.widgets.spinBoxCropTop.value()
        else:
            crop_top_px = int(self.widgets.spinBoxCropTop.value() * 0.01 * image_size.height())

        return crop_top_px

    def get_crop_value_bottom(self):
        image_size = self.current_pixmap.size()

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

        if self.image_location is None:
            pass

        self.checkVisibility()

        scaled_pix_size = self.graphics_pixmap.pixmap().size()
        scale_x = scaled_pix_size.width() / self.image_width
        scale_y = scaled_pix_size.height() / self.image_height

        crop_left_px, crop_right_px, crop_top_px, crop_bottom_px = self.get_crop_values(scale_factor_x=scale_x, scale_factor_y=scale_y)

        crop_right_pos = int(scaled_pix_size.width() - crop_right_px)
        crop_bottom_pos = int(scaled_pix_size.height() - crop_bottom_px)


        print("Crop px (top, bottom, left, right): ", crop_top_px, crop_bottom_pos, crop_left_px, crop_right_pos)
        widget_size = self.widgets.graphicsView.size()


        image_y_top = self.dy
        image_y_bottom = widget_size.height() - self.dy

        image_x_left = self.dx
        image_x_right = widget_size.width() - self.dx

        crop_y_top = image_y_top + crop_top_px
        crop_y_bottom = image_y_bottom - crop_bottom_px

        crop_x_left = image_x_left + crop_left_px
        crop_x_right = image_x_right - crop_right_px

        rect_top_TL = QPointF(image_x_left, image_y_top)
        rect_top_BR = QPointF(image_x_right, crop_y_top)

        rect_bottom_TL = QPointF(image_x_left, crop_y_bottom)
        rec_bottom_BR = QPointF(image_x_right, image_y_bottom)

        rect_left_TL = QPointF(image_x_left, crop_y_top)
        rect_left_BR = QPointF(crop_x_left, crop_y_bottom)

        rect_right_TL = QPointF(crop_x_right, crop_y_top)
        rect_right_BR = QPointF(image_x_right, crop_y_bottom)

        self.graphics_crop_rect_top.setRect(QRectF(rect_top_TL, rect_top_BR))
        self.graphics_crop_rect_bottom.setRect(QRectF(rect_bottom_TL, rec_bottom_BR))
        self.graphics_crop_rect_left.setRect(QRectF(rect_left_TL, rect_left_BR))
        self.graphics_crop_rect_right.setRect(QRectF(rect_right_TL, rect_right_BR))
        
        point_line_TL = QPointF(crop_x_left, crop_y_top)
        point_line_TR = QPointF(crop_x_right, crop_y_top)
        point_line_BR = QPointF(crop_x_right, crop_y_bottom)
        point_line_BL = QPointF(crop_x_left, crop_y_bottom)

        line_top = QLineF(point_line_TL, point_line_TR)
        line_bottom = QLineF(point_line_BL, point_line_BR)
        line_left = QLineF(point_line_TL, point_line_BL)
        line_right = QLineF(point_line_TR, point_line_BR)

        self.graphics_crop_line_full_bottom.setLine(line_bottom)
        self.graphics_crop_line_full_top.setLine(line_top)
        self.graphics_crop_line_full_left.setLine(line_left)
        self.graphics_crop_line_full_right.setLine(line_right)

        self.graphics_crop_line_dot_bottom.setLine(line_bottom)
        self.graphics_crop_line_dot_top.setLine(line_top)
        self.graphics_crop_line_dot_left.setLine(line_left)
        self.graphics_crop_line_dot_right.setLine(line_right)


    def resizeEvent(self, *args, **kwargs):
        super().resizeEvent(*args, **kwargs)
        print("resize event")
        self.fix_image_size()

    def fix_image_size(self):
        if self.image_location is not None:
            pix_size = self.current_pixmap.scaled(self.widgets.graphicsView.size(), aspectRatioMode=1)
            print("scene: ", self.graphics.sceneRect())
            self.dx = (self.widgets.graphicsView.size().width() - pix_size.size().width())/2
            self.dy = (self.widgets.graphicsView.size().height() - pix_size.size().height())/2
            print("dx: ", self.dx, " dy: ", self.dy, " size graphics: ", self.widgets.graphicsView.size(), " scaled pix: ", pix_size.size())
            print("current offset: ", self.graphics_pixmap.offset())
            self.graphics_pixmap.setPixmap(pix_size)
            self.graphics_pixmap.setOffset(QPointF(self.dx,self.dy))
            print("new offset: ", self.graphics_pixmap.offset())
            self.changeCrop()

    def set_image(self, location):
        print("setting image from: ", location)
        self.image_location = location
        self.current_pixmap = QPixmap(QImage(location))
        image_size = self.current_pixmap.size()
        self.image_height = image_size.height()
        self.image_width = image_size.width()

        self.widgets.spinBoxCropBottom.setMaximum(self.image_height)
        self.widgets.spinBoxCropTop.setMaximum(self.image_height)

        self.widgets.spinBoxCropRight.setMaximum(self.image_width)
        self.widgets.spinBoxCropLeft.setMaximum(self.image_width)

        if self.graphics_pixmap is None:
            self.graphics_pixmap = self.graphics.addPixmap(self.current_pixmap)
            self.graphics_pixmap.setZValue(-1)
            self.fix_image_size()
        else:
            self.fix_image_size()

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

def createPDF(image, margin_x_mm, margin_y_mm, desired_mm, desired_direction, marking, page_rotation, pdf_name):
    """ Divides image over multiple pdf pages according to the parameters """
    A4_width = 210  # mm
    A4_height = 297  # mm

    printer = QPrinter(mode=QPrinter.HighResolution)
    printer.setOutputFileName(pdf_name)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setFullPage(True)
    printer.setPaperSize(QPrinter.A4)

    mark_function = drawNothing

    if marking == "fullCross":
        mark_function = drawFullCross
    if marking == "halfCross":
        mark_function = drawHalfCross
    if marking == "fullLine":
        mark_function = drawFullLine

    painter = QPainter()
    painter.begin(printer)

    # instead of using a different function, just rotate the image and change the disired direction
    if page_rotation == "horizontal":
        transform = QTransform()
        transform.rotate(90)
        image = image.transformed(transform)
        if desired_direction == "wide":
            desired_direction = "heigh"
        else:
            desired_direction = "wide"

    im_size = image.size()
    im_width = im_size.width()
    im_height = im_size.height()
    im_ratio = im_width / im_height

    if desired_direction == "wide":
        des_x_mm = desired_mm
        des_y_mm = des_x_mm * (1 / im_ratio)
    else:
        des_y_mm = desired_mm
        des_x_mm = des_y_mm * im_ratio

    pdf_x_px = printer.width()
    pdf_y_px = printer.height()

    # available pixels in x and y direction
    av_x_mm = A4_width - 2 * margin_x_mm
    av_y_mm = A4_height - 2 * margin_y_mm

    margin_x_px = (margin_x_mm / A4_width) * pdf_x_px
    margin_y_px = (margin_y_mm / A4_height) * pdf_y_px

    av_x_px = (av_x_mm / A4_width) * pdf_x_px
    av_y_px = (av_y_mm / A4_height) * pdf_y_px

    amount_x = des_x_mm / av_x_mm
    amount_y = des_y_mm / av_y_mm

    seg_im_x_px = im_width / amount_x
    seg_im_y_px = im_height / amount_y

    amount_whole_x = int(math.floor(amount_x))
    amount_rest_x = amount_x - amount_whole_x
    target_rest_x_px = amount_rest_x * av_x_px
    source_rest_x_px = im_width - amount_whole_x * seg_im_x_px

    amount_whole_y = int(math.floor(amount_y))
    amount_rest_y = amount_y - amount_whole_y
    target_rest_y_px = amount_rest_y * av_y_px
    source_rest_y_px = im_height - amount_whole_y * seg_im_y_px

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
    if source_rest_y_px != 0:
        for x in range(amount_whole_x):
            target_top_left = QPoint(margin_x_px, margin_y_px)
            target_bottom_right = QPoint(margin_x_px + av_x_px, margin_y_px + target_rest_y_px)

            source_top_left = QPoint(x * seg_im_x_px, amount_whole_y * seg_im_y_px)
            source_bottom_right = QPoint((x + 1) * seg_im_x_px, amount_whole_y * seg_im_y_px + source_rest_y_px)

            rect_target = QRect(target_top_left, target_bottom_right)
            rect_source = QRect(source_top_left, source_bottom_right)

            painter.drawImage(rect_target, image, rect_source)

            mark_function(target_top_left, target_bottom_right, margin_x_px, margin_y_px, pdf_x_px, pdf_y_px, painter)

            printer.newPage()

    # print the partial pages in the x direction
    if source_rest_x_px != 0:
        for y in range(amount_whole_y):
            target_top_left = QPoint(margin_x_px, margin_y_px)
            target_bottom_right = QPoint(margin_x_px + target_rest_x_px, margin_y_px + av_y_px)

            source_top_left = QPoint(amount_whole_x * seg_im_x_px, y * seg_im_y_px)
            source_bottom_right = QPoint(amount_whole_x * seg_im_x_px + source_rest_x_px, (y + 1) * seg_im_y_px)

            rect_target = QRect(target_top_left, target_bottom_right)
            rect_source = QRect(source_top_left, source_bottom_right)

            painter.drawImage(rect_target, image, rect_source)

            mark_function(target_top_left, target_bottom_right, margin_x_px, margin_y_px, pdf_x_px, pdf_y_px, painter)

            printer.newPage()

    # print the corner consisting of both partial pages
    if source_rest_x_px != 0 and source_rest_y_px != 0:
        target_top_left = QPoint(margin_x_px, margin_y_px)
        target_bottom_right = QPoint(margin_x_px + target_rest_x_px, margin_y_px + target_rest_y_px)

        source_top_left = QPoint((amount_whole_x + 1) * seg_im_x_px, (amount_whole_y + 1) * seg_im_y_px)
        source_bottom_right = QPoint((amount_whole_x + 1) * seg_im_x_px + source_rest_x_px,
                                     (amount_whole_y + 1) * seg_im_y_px + source_rest_y_px)

        rect_target = QRect(target_top_left, target_bottom_right)
        rect_source = QRect(source_top_left, source_bottom_right)

        painter.drawImage(rect_target, image, rect_source)

        mark_function(target_top_left, target_bottom_right, margin_x_px, margin_y_px, pdf_x_px, pdf_y_px, painter)

    painter.end()

if __name__ == "__main__":
    monitor_width = 1920
    monitor_height = 1080

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MyUI()
    ui = Ui_MainWindow()

    ui.setupUi(MainWindow)
    MainWindow.confirmUI(ui)
    #MainWindow.set_image(image_location)

    MainWindow.show()
    sys.exit(app.exec_())