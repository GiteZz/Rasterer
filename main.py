import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QColor, QPainter, QPen, QTransform
from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtPrintSupport import QPrinter
from ui import Ui_MainWindow
import math
from screeninfo import get_monitors

image_location = "C:/Users/Gilles/Pictures/TestImages/falcon9morning.jpg"

def button_test():

    print("Hello World!")

class MyUI(QtWidgets.QMainWindow):
    def __init__(self, monitor_width, monitor_height):
        super().__init__()
        self.co_crop_top = (0,0)
        self.cc_crop_bottom = (0,0)
        self.added_image = False
        self.margin_width = 0.05 * monitor_width
        self.margin_height = 0.05 * monitor_height
        self.textbox_width = 0.1 * monitor_width
        self.widgets = None
        self.addCropMarks = False
        self.current_pixmap = None
        self.color_background = QColor(125,125,125, 100)

        self.lock_crop_TB = False
        self.lock_crop_LR = False

        self.image_location = "C:/Users/Gilles/Pictures/TestImages/falcon9morning.jpg"

    def confirmUI(self, ui_widgets):
        self.widgets = ui_widgets
        self.widgets.spinBoxCropTop.valueChanged.connect(self.changeCropTop)
        self.widgets.spinBoxCropBottom.valueChanged.connect(self.changeCropBottom)
        self.widgets.spinBoxCropLeft.valueChanged.connect(self.changeCropLeft)
        self.widgets.spinBoxCropRight.valueChanged.connect(self.changeCropRight)

        ui.checkBoxLockLR.stateChanged.connect(self.lockCheckBoxChanged)
        ui.checkBoxLockTB.stateChanged.connect(self.lockCheckBoxChanged)

        ui.pushButtonCreatePDF.clicked.connect(self.pdf_button)

    def pdf_button(self):
        image_non_cropped = QImage(self.image_location)
        im_size = image_non_cropped.size()
        crop_top_left = QPoint(self.widgets.spinBoxCropLeft.value(), self.widgets.spinBoxCropTop.value())
        crop_bottom_right = QPoint(im_size.width() - self.widgets.spinBoxCropRight.value(), im_size.height() - self.widgets.spinBoxCropBottom.value())

        image_cropped = image_non_cropped.copy(QRect(crop_top_left, crop_bottom_right))
        # (image, margin_x_mm, margin_y_mm, desired_mm, desired_direction, marking, page_rotation, pdf_name)

        marking = ["halfCross", "fullCross", "fullLine", "nothing"][self.widgets.comboBoxMarking.currentIndex()]
        createPDF(image_cropped,
                  self.widgets.spinBoxPDFMarginX.value(), self.widgets.spinBoxPDFMarginY.value(),
                  self.widgets.spinBoxDesiredSize.value(), self.widgets.comboBoxDesiredAxis.currentText(),
                  marking, self.widgets.comboBoxPageRotation.currentText(), "new.pdf")

    def lockCheckBoxChanged(self):
        self.lock_crop_TB = ui.checkBoxLockTB.isChecked()
        self.lock_crop_LR = ui.checkBoxLockLR.isChecked()

    def changeCropLeft(self):
        if self.lock_crop_LR:
            ui.spinBoxCropRight.setValue(ui.spinBoxCropLeft.value())
        self.changeCrop()

    def changeCropRight(self):
        if self.lock_crop_LR:
            ui.spinBoxCropLeft.setValue(ui.spinBoxCropRight.value())
        self.changeCrop()

    def changeCropTop(self):
        if self.lock_crop_TB:
            ui.spinBoxCropBottom.setValue(ui.spinBoxCropTop.value())
        self.changeCrop()

    def changeCropBottom(self):
        if self.lock_crop_TB:
            ui.spinBoxCropTop.setValue(ui.spinBoxCropBottom.value())
        self.changeCrop()

    def changeCrop(self):
        print("crop changed")
        if self.widgets.spinBoxCropBottom.value() != 0 \
           or self.widgets.spinBoxCropTop.value() != 0 \
           or self.widgets.spinBoxCropLeft.value() != 0 \
           or self.widgets.spinBoxCropRight.value() != 0:
            self.addCropMarks = True
        else:
            self.addCropMarks = False

        widget_size = self.widgets.mainImageLabel.size()

        image_size = self.pixmap.size()

        rel_crop_left = int((self.widgets.spinBoxCropLeft.value() / image_size.width()) * widget_size.width())
        rel_crop_right = int((self.widgets.spinBoxCropRight.value() / image_size.width()) * widget_size.width())

        rel_crop_top = int((self.widgets.spinBoxCropTop.value() / image_size.height()) * widget_size.height())
        rel_crop_bottom = int((self.widgets.spinBoxCropBottom.value() / image_size.height()) * widget_size.height())

        bottom_right = QPoint(widget_size.width(),widget_size.height())

        point_rect_top_bottom = QPoint(widget_size.width(),rel_crop_top)
        self.rect_top = QRect(QPoint(0,0), point_rect_top_bottom)

        point_rect_bottom_top = QPoint(0, bottom_right.y() - rel_crop_bottom)
        self.rect_bottom = QRect(point_rect_bottom_top, bottom_right)

        point_rect_left_bottom = QPoint(rel_crop_left, widget_size.height() - rel_crop_bottom)
        self.rect_left = QRect(QPoint(0,rel_crop_top), point_rect_left_bottom)

        point_rect_right_top = QPoint(widget_size.width() - rel_crop_right, rel_crop_top)
        point_rect_right_bottom = QPoint(widget_size.width(), widget_size.height() - rel_crop_bottom)
        self.rect_right = QRect(point_rect_right_top, point_rect_right_bottom)

    def paintEvent(self, *args, **kwargs):
        print("Paint Event")
        new_pixmap = QPixmap(self.current_pixmap)
        qp = QtGui.QPainter(new_pixmap)
        qp.begin(self)
        if self.addCropMarks:
            qp.fillRect(self.rect_bottom, self.color_background)
            qp.fillRect(self.rect_top, self.color_background)
            qp.fillRect(self.rect_left, self.color_background)
            qp.fillRect(self.rect_right, self.color_background)

        self.widgets.mainImageLabel.setPixmap(new_pixmap)
        qp.end()

    def resizeEvent(self, *args, **kwargs):
        super().resizeEvent(*args, **kwargs)
        print("resize event")

        #handle inputtext
        if self.added_image:
            pix_size = self.pixmap.scaled(self.widgets.mainImageLabel.size())
            self.widgets.mainImageLabel.setPixmap(pix_size)
            self.current_pixmap = pix_size

    def set_image(self, location):
        self.added_image = True

        image = QImage(location)
        self.pixmap = QPixmap.fromImage(image)
        pix_size = self.pixmap.scaled(self.widgets.mainImageLabel.size())
        self.widgets.mainImageLabel.setPixmap(pix_size)
        self.current_pixmap = pix_size


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
    MainWindow = MyUI(monitor_width, monitor_height)
    ui = Ui_MainWindow()

    ui.setupUi(MainWindow)
    MainWindow.confirmUI(ui)
    MainWindow.set_image(image_location)

    MainWindow.show()
    sys.exit(app.exec_())