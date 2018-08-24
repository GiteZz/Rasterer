import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QColor, QPainter, QPen, QTransform, QBrush
from PyQt5.QtCore import QPoint, QRect, QPointF, QRectF, QLineF
from PyQt5.QtWidgets import QGraphicsScene, QFileDialog
from PyQt5.QtPrintSupport import QPrinter
from ui import Ui_MainWindow
import math
import logging

class graphicsHelper:
    def __init__(self, widget, crop_rect=None, pixmap=None):
        self.original_pix = pixmap
        self.scaled_pix = pixmap
        self.cropped_pix = pixmap

        self.widget = widget

        self.widget_x_px = None
        self.widget_y_px = None
        self.im_x_px = None
        self.im_y_px = None

        self.crop_rect = crop_rect

        self.graphics = QGraphicsScene()
        self.widget.setScene(self.graphics)

        self.widget.setHorizontalScrollBarPolicy(1)
        self.widget.setVerticalScrollBarPolicy(1)

        if pixmap is not None:
            self.graphics_pixmap = self.graphics.addPixmap(pixmap)
        else:
            self.graphics_pixmap = None

        self.update()

    def update(self):
        self.widget_size = self.widget.size()
        self.widget_x_px = self.widget_size.width()
        self.widget_y_px = self.widget_size.height()

        if self.original_pix is not None:
            self.update_image_info()

    def update_image_info(self):
        widget_size = self.widget.size()

        if self.crop_rect is not None:
            self.cropped_pix = self.original_pix.copy(self.crop_rect)
        else:
            self.cropped_pix = self.original_pix

        self.scaled_pix = self.cropped_pix.scaled(widget_size, aspectRatioMode=1)

        image_size = self.scaled_pix.size()
        self.im_x_px = image_size.width()
        self.im_y_px = image_size.height()

        self.offset_x_px = int((self.widget_x_px - self.im_x_px) / 2)
        self.offset_y_px = int((self.widget_y_px - self.im_y_px) / 2)

        if self.graphics_pixmap is not None:
            self.graphics_pixmap.setPixmap(self.scaled_pix)
        else:
            self.graphics_pixmap = self.graphics.addPixmap(self.scaled_pix)
            self.graphics_pixmap.setZValue(-1)

        self.graphics_pixmap.setOffset(QPointF(self.offset_x_px, self.offset_y_px))

    def set_image(self, location):
        self.original_pix = QPixmap(QImage(location))
        self.update_image_info()

class graphicsCrop(graphicsHelper):
    def __init__(self, widget, crop_rect=None, pixmap=None):
        super().__init__(widget, crop_rect=crop_rect, pixmap=pixmap)

        self.crop_left_px = None
        self.crop_right_px = None
        self.crop_top_px = None
        self.crop_bottom_px = None

        # used to create dummy rectangles
        TL = QPoint(0, 0)
        BR = QPoint(0, 0)

        # draw the rectangles in a see through black
        brush = QBrush(QColor(0, 0, 0, 50))

        # create pen that draws nothing, used for rectangles without border
        empty_pen = QPen(QColor(0, 0, 0, 255))
        empty_pen.setStyle(0)

        # these two together create a white/black dotted line
        full_pen = QPen(QColor(255, 255, 255))
        dot_pen = QPen(QColor(0, 0, 0))
        dot_pen.setStyle(3)

        self.graphics_crop_rect_bottom = self.graphics.addRect(QRectF(TL, BR), brush=brush, pen=empty_pen)
        self.graphics_crop_rect_top = self.graphics.addRect(QRectF(TL, BR), brush=brush, pen=empty_pen)
        self.graphics_crop_rect_left = self.graphics.addRect(QRectF(TL, BR), brush=brush, pen=empty_pen)
        self.graphics_crop_rect_right = self.graphics.addRect(QRectF(TL, BR), brush=brush, pen=empty_pen)

        self.graphics_crop_line_full_bottom = self.graphics.addLine(QLineF(TL, BR), pen=full_pen)
        self.graphics_crop_line_full_top = self.graphics.addLine(QLineF(TL, BR), pen=full_pen)
        self.graphics_crop_line_full_left = self.graphics.addLine(QLineF(TL, BR), pen=full_pen)
        self.graphics_crop_line_full_right = self.graphics.addLine(QLineF(TL, BR), pen=full_pen)

        self.graphics_crop_line_dot_bottom = self.graphics.addLine(QLineF(TL, BR), pen=dot_pen)
        self.graphics_crop_line_dot_top = self.graphics.addLine(QLineF(TL, BR), pen=dot_pen)
        self.graphics_crop_line_dot_left = self.graphics.addLine(QLineF(TL, BR), pen=dot_pen)
        self.graphics_crop_line_dot_right = self.graphics.addLine(QLineF(TL, BR), pen=dot_pen)

    def check_visibility(self, crop_left_px, crop_right_px, crop_top_px, crop_bottom_px):
        self.graphics_crop_line_full_bottom.setVisible(crop_bottom_px != 0)
        self.graphics_crop_line_dot_bottom.setVisible(crop_bottom_px != 0)
        self.graphics_crop_rect_bottom.setVisible(crop_bottom_px != 0)

        self.graphics_crop_line_full_top.setVisible(crop_top_px != 0)
        self.graphics_crop_line_dot_top.setVisible(crop_top_px != 0)
        self.graphics_crop_rect_top.setVisible(crop_top_px != 0)

        self.graphics_crop_line_full_right.setVisible(crop_right_px != 0)
        self.graphics_crop_line_dot_right.setVisible(crop_right_px != 0)
        self.graphics_crop_rect_right.setVisible(crop_right_px != 0)

        self.graphics_crop_line_full_left.setVisible(crop_left_px != 0)
        self.graphics_crop_line_dot_left.setVisible(crop_left_px != 0)
        self.graphics_crop_rect_left.setVisible(crop_left_px != 0)

    def change_crop(self, crop_left_px, crop_right_px, crop_top_px, crop_bottom_px):
        self.check_visibility(crop_left_px, crop_right_px, crop_top_px, crop_bottom_px)
        scale_x = self.scaled_pix.size().width() / self.im_x_px
        scale_y = self.scaled_pix.size().height() / self.im_y_px

        crop_left_px *= scale_x
        crop_right_px *= scale_x

        crop_top_px *= scale_y
        crop_bottom_px *= scale_y

        self.crop_left_px = crop_left_px
        self.crop_right_px = crop_right_px
        self.crop_top_px = crop_top_px
        self.crop_bottom_px = crop_bottom_px

        image_y_top = self.offset_y_px
        image_y_bottom = self.widget_y_px - self.offset_y_px

        image_x_left = self.offset_x_px
        image_x_right = self.widget_x_px - self.offset_x_px

        crop_y_top = image_y_top + crop_top_px
        crop_y_bottom = image_y_bottom - crop_bottom_px

        crop_x_left = image_x_left + crop_left_px
        crop_x_right = image_x_right - crop_right_px

        # these are the coordinates that contain the cropped image relative to the graphicsViewFullImage
        rect_top_TL = QPointF(image_x_left, image_y_top)
        rect_top_BR = QPointF(image_x_right, crop_y_top)

        rect_bottom_TL = QPointF(image_x_left, crop_y_bottom)
        rec_bottom_BR = QPointF(image_x_right, image_y_bottom)

        rect_left_TL = QPointF(image_x_left, crop_y_top)
        rect_left_BR = QPointF(crop_x_left, crop_y_bottom)

        rect_right_TL = QPointF(crop_x_right, crop_y_top)
        rect_right_BR = QPointF(image_x_right, crop_y_bottom)

        # the top/bottom rect fill the whole width of the image
        # the left/right only fill in the range between the top and bottom rect
        # this is used to not have overlapping rects mess up the alpha
        self.graphics_crop_rect_top.setRect(QRectF(rect_top_TL, rect_top_BR))
        self.graphics_crop_rect_bottom.setRect(QRectF(rect_bottom_TL, rec_bottom_BR))
        self.graphics_crop_rect_left.setRect(QRectF(rect_left_TL, rect_left_BR))
        self.graphics_crop_rect_right.setRect(QRectF(rect_right_TL, rect_right_BR))

        # the coordinates are uses to draw al line between the section that gets cropped away
        # and the section that stays
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