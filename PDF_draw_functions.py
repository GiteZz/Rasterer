from PyQt5.QtGui import QImage, QPixmap, QColor, QPainter, QPen, QTransform, QBrush, QIcon
from PyQt5.QtCore import QPoint, QRect, QPointF, QRectF, QLineF, QSize
import math


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