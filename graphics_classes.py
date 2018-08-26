import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QColor, QPainter, QPen, QTransform, QBrush
from PyQt5.QtCore import QPoint, QRect, QPointF, QRectF, QLineF, QSize, QSizeF
from PyQt5.QtWidgets import QGraphicsScene, QFileDialog
from PyQt5.QtPrintSupport import QPrinter
from ui import Ui_MainWindow
import math
import logging

class graphicsHelper:
    def __init__(self, widget, pixmap=None, crop_image=True, show_image=True):
        self.original_pix = pixmap
        self.scaled_pix = pixmap
        self.cropped_pix = pixmap

        self.widget = widget

        self.crop_image = crop_image

        self.crop_left_px = None
        self.crop_right_px = None
        self.crop_bottom_px = None
        self.crop_top_px = None

        self.graphics = QGraphicsScene()
        self.widget.setScene(self.graphics)

        self.widget.setHorizontalScrollBarPolicy(1)
        self.widget.setVerticalScrollBarPolicy(1)

        self.im_x_px = None
        self.im_y_px = None

        self.show_image = show_image

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
            self.update_tab_function()

    def change_crop(self, crop_left_px, crop_right_px, crop_top_px, crop_bottom_px):
        self.crop_bottom_px = crop_bottom_px
        self.crop_top_px = crop_top_px
        self.crop_left_px = crop_left_px
        self.crop_right_px = crop_right_px

        self.update()

    def get_crop_rect(self):
        image_size = self.original_pix.size()
        im_x_px = image_size.width()
        im_y_px = image_size.height()

        rect_TL = QPoint(self.crop_left_px, self.crop_top_px)
        rect_BR = QPoint(im_x_px - self.crop_right_px, im_y_px - self.crop_bottom_px)

        return QRect(rect_TL, rect_BR)

    def update_image_info(self):
        self.image_size = self.original_pix.size()
        self.im_x_px = self.image_size.width()
        self.im_y_px = self.image_size.height()

        if self.crop_right_px is not None:
            crop_rect = self.get_crop_rect()
            self.cropped_pix = self.original_pix.copy(crop_rect)
        else:
            self.cropped_pix = self.original_pix

        if self.crop_image:
            self.scaled_pix = self.cropped_pix.scaled(self.widget_size, aspectRatioMode=1)
        else:
            self.scaled_pix = self.original_pix.scaled(self.widget_size, aspectRatioMode=1)

        image_size = self.scaled_pix.size()
        self.scaled_im_x_px = image_size.width()
        self.scaled_im_y_px = image_size.height()

        self.offset_x_px = int((self.widget_x_px - self.scaled_im_x_px) / 2)
        self.offset_y_px = int((self.widget_y_px - self.scaled_im_y_px) / 2)

        if self.graphics_pixmap is not None:
            self.graphics_pixmap.setPixmap(self.scaled_pix)
        else:
            self.graphics_pixmap = self.graphics.addPixmap(self.scaled_pix)
            self.graphics_pixmap.setZValue(-1)

        self.graphics_pixmap.setOffset(QPointF(self.offset_x_px, self.offset_y_px))
        self.graphics_pixmap.setVisible(self.show_image)

    def set_image(self, location):
        self.original_pix = QPixmap(QImage(location))
        self.update_image_info()

    def update_tab_function(self):
        pass

class graphicsCrop(graphicsHelper):
    def __init__(self, widget, pixmap=None):
        super().__init__(widget, pixmap=pixmap, crop_image=False)

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

    def check_visibility(self):
        self.graphics_crop_line_full_bottom.setVisible(self.crop_bottom_px != 0)
        self.graphics_crop_line_dot_bottom.setVisible(self.crop_bottom_px != 0)
        self.graphics_crop_rect_bottom.setVisible(self.crop_bottom_px != 0)

        self.graphics_crop_line_full_top.setVisible(self.crop_top_px != 0)
        self.graphics_crop_line_dot_top.setVisible(self.crop_top_px != 0)
        self.graphics_crop_rect_top.setVisible(self.crop_top_px != 0)

        self.graphics_crop_line_full_right.setVisible(self.crop_right_px != 0)
        self.graphics_crop_line_dot_right.setVisible(self.crop_right_px != 0)
        self.graphics_crop_rect_right.setVisible(self.crop_right_px != 0)

        self.graphics_crop_line_full_left.setVisible(self.crop_left_px != 0)
        self.graphics_crop_line_dot_left.setVisible(self.crop_left_px != 0)
        self.graphics_crop_rect_left.setVisible(self.crop_left_px != 0)

    def update_tab_function(self):
        if self.crop_left_px is None:
            return

        self.check_visibility()
        scale_x = self.scaled_pix.size().width() / self.im_x_px
        scale_y = self.scaled_pix.size().height() / self.im_y_px

        crop_left_scale_px = self.crop_left_px * scale_x
        crop_right_scale_px = self.crop_right_px * scale_x

        crop_top_scale_px = self.crop_top_px * scale_y
        crop_bottom_scale_px = self.crop_bottom_px * scale_y

        image_y_top = self.offset_y_px
        image_y_bottom = self.widget_y_px - self.offset_y_px

        image_x_left = self.offset_x_px
        image_x_right = self.widget_x_px - self.offset_x_px

        crop_y_top = image_y_top + crop_top_scale_px
        crop_y_bottom = image_y_bottom - crop_bottom_scale_px

        crop_x_left = image_x_left + crop_left_scale_px
        crop_x_right = image_x_right - crop_right_scale_px

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

class graphicsPDF(graphicsHelper):
    def __init__(self, widget, pixmap=None):
        super().__init__(widget, pixmap=pixmap, crop_image=False, show_image=False)
        self.A4_x_mm = 210
        self.A4_y_mm = 297

        self.paper_list = []

        self.brush = QBrush(QColor(0, 0, 0, 0))

    def update_pdf_values(self, des_size_mm, width, margin_x_mm, margin_y_mm, A4_vertical):
        # clear items
        self.des_size_mm = des_size_mm
        self.width = width
        self.margin_x_mm = margin_x_mm
        self.margin_y_mm = margin_y_mm
        self.A4_vertical = A4_vertical


        for item in self.paper_list:
            self.graphics.removeItem(item)
        self.paper_list = []

        A4_av_x_mm = self.A4_x_mm - 2 * margin_x_mm
        A4_av_y_mm = self.A4_y_mm - 2 * margin_y_mm

        im_x_px = self.cropped_pix.size().width()
        im_y_px = self.cropped_pix.size().height()

        if width:
            des_size_x_mm = des_size_mm
            des_size_y_mm = (im_y_px / im_x_px) * des_size_x_mm
        else:
            des_size_y_mm = des_size_mm
            des_size_x_mm = (im_x_px / im_y_px) * des_size_y_mm

        crop_im_ratio = im_x_px / im_y_px
        widget_ratio = self.widget_x_px / self.widget_y_px
        A4_ratio = self.A4_x_mm / self.A4_y_mm

        # if vertical is true the image spans across normal places A4's otherwise across horizontal A4's
        if A4_vertical:
            des_A4_x = des_size_x_mm / A4_av_x_mm
            des_A4_y = des_size_y_mm / A4_av_y_mm

            margin_fac_x = margin_x_mm / self.A4_x_mm
            margin_fac_y = margin_y_mm / self.A4_y_mm
        else:
            des_A4_x = des_size_x_mm / A4_av_y_mm
            des_A4_y = des_size_y_mm / A4_av_x_mm

            A4_ratio = 1 / A4_ratio

            margin_fac_y = margin_x_mm / self.A4_x_mm
            margin_fac_x = margin_y_mm / self.A4_y_mm

        paint_ratio = (math.ceil(des_A4_x)/math.ceil(des_A4_y)) * A4_ratio

        if widget_ratio > paint_ratio:
            # height is limiting factor
            A4_rect_y_px = self.widget_y_px / math.ceil(des_A4_y)
            A4_rect_x_px = A4_rect_y_px * A4_ratio
            dy = 0
            dx = (self.widget_x_px - math.ceil(des_A4_x) * A4_rect_x_px) / 2
        else:
            A4_rect_x_px = self.widget_x_px / math.ceil(des_A4_x)
            A4_rect_y_px = A4_rect_x_px * (1 / A4_ratio)
            dx = 0
            dy = (self.widget_y_px - math.ceil(des_A4_y) * A4_rect_y_px) / 2

        des_A4_x_whole = math.floor(des_A4_x)
        des_A4_y_whole = math.floor(des_A4_y)

        des_A4_x_rem = des_A4_x - des_A4_x_whole
        des_A4_y_rem = des_A4_y - des_A4_y_whole

        margin_x_px = margin_fac_x * A4_rect_x_px
        margin_y_px = margin_fac_y * A4_rect_y_px

        A4_body_x_px = int(A4_rect_x_px - 2 * margin_x_px)
        A4_body_y_px = int(A4_rect_y_px - 2 * margin_y_px)

        A4_rem_x_px = (des_A4_x - des_A4_x_whole) * A4_body_x_px
        A4_rem_y_px = (des_A4_y - des_A4_y_whole) * A4_rect_y_px

        im_seg_x_px = im_x_px / des_A4_x
        im_seg_y_px = im_y_px / des_A4_y

        im_rem_x_px = im_x_px - des_A4_x_whole * im_seg_x_px
        im_rem_y_px = im_y_px - des_A4_y_whole * im_seg_y_px

        for x in range(des_A4_x_whole):
            for y in range(des_A4_y_whole):
                x_left_px = dx + x * A4_rect_x_px + margin_x_px
                y_top_px = dy + y * A4_rect_y_px + margin_y_px

                pos_TL = QPointF(x_left_px, y_top_px)



                scene_dest = QPointF(x_left_px, y_top_px)

                TL = QPoint(x * im_seg_x_px, y * im_seg_y_px)
                BR = QPoint((x + 1) * im_seg_x_px, (y + 1) * im_seg_y_px)

                crop_rect = QRect(TL, BR)

                size_A4 = QSize(A4_body_x_px, A4_body_y_px)

                image_piece = self.cropped_pix.copy(crop_rect)
                image_sized = image_piece.scaled(size_A4)

                current_page = self.graphics.addPixmap(image_sized)
                current_page.setOffset(pos_TL)
                self.paper_list.append(current_page)

                page_TL = QPointF(x_left_px - margin_x_px, y_top_px - margin_y_px)
                page_BR = QPointF(x_left_px + A4_body_x_px + margin_x_px, y_top_px + A4_body_y_px + margin_y_px)

                page = self.graphics.addRect(QRectF(page_TL, page_BR))
                self.paper_list.append(page)

        if im_rem_x_px != 0:
            for y in range(des_A4_y_whole):
                x_left_px = dx + des_A4_x_whole * A4_rect_x_px + margin_x_px

                y_top_px = dy + y * A4_rect_y_px + margin_y_px

                pos_TL = QPointF(x_left_px, y_top_px)

                scene_dest = QPointF(x_left_px, y_top_px)

                TL = QPoint(des_A4_x_whole * im_seg_x_px, y * im_seg_y_px)
                BR = QPoint(des_A4_x_whole * im_seg_x_px + im_rem_x_px, (y + 1) * im_seg_y_px)

                crop_rect = QRect(TL, BR)

                size_A4 = QSize(A4_body_x_px, A4_body_y_px)

                image_piece = self.cropped_pix.copy(crop_rect)
                image_sized = image_piece.scaled(size_A4, aspectRatioMode=1)

                current_page = self.graphics.addPixmap(image_sized)
                current_page.setOffset(pos_TL)
                self.paper_list.append(current_page)

                page_TL = QPointF(x_left_px - margin_x_px, y_top_px - margin_y_px)
                page_BR = QPointF(x_left_px + A4_body_x_px + margin_x_px, y_top_px + A4_body_y_px + margin_y_px)

                page = self.graphics.addRect(QRectF(page_TL, page_BR))
                self.paper_list.append(page)

        if im_rem_y_px != 0:
            for x in range(des_A4_x_whole):
                x_left_px = dx + x * A4_rect_x_px + margin_x_px

                y_top_px = dy + des_A4_y_whole * A4_rect_y_px + margin_y_px

                pos_TL = QPointF(x_left_px, y_top_px)

                scene_dest = QPointF(x_left_px, y_top_px)

                TL = QPoint(x * im_seg_x_px, des_A4_y_whole * im_seg_y_px)
                BR = QPoint((x + 1) * im_seg_x_px, des_A4_y_whole * im_seg_y_px + im_rem_y_px)

                crop_rect = QRect(TL, BR)

                size_A4 = QSize(A4_body_x_px, A4_body_y_px)

                image_piece = self.cropped_pix.copy(crop_rect)
                image_sized = image_piece.scaled(size_A4, aspectRatioMode=1)

                current_page = self.graphics.addPixmap(image_sized)
                current_page.setOffset(pos_TL)
                self.paper_list.append(current_page)

                page_TL = QPointF(x_left_px - margin_x_px, y_top_px - margin_y_px)
                page_BR = QPointF(x_left_px + A4_body_x_px + margin_x_px, y_top_px + A4_body_y_px + margin_y_px)

                page = self.graphics.addRect(QRectF(page_TL, page_BR))
                self.paper_list.append(page)

        if im_rem_y_px != 0 and im_rem_x_px != 0:
            x_left_px = dx + des_A4_x_whole * A4_rect_x_px + margin_x_px

            y_top_px = dy + des_A4_y_whole * A4_rect_y_px + margin_y_px

            pos_TL = QPointF(x_left_px, y_top_px)

            scene_dest = QPointF(x_left_px, y_top_px)

            TL = QPoint(des_A4_x_whole * im_seg_x_px, des_A4_y_whole * im_seg_y_px)
            BR = QPoint(des_A4_x_whole * im_seg_x_px + im_rem_x_px, des_A4_y_whole * im_seg_y_px + im_rem_y_px)

            crop_rect = QRect(TL, BR)

            size_A4 = QSize(A4_rem_x_px, A4_rem_y_px)

            image_piece = self.cropped_pix.copy(crop_rect)
            image_sized = image_piece.scaled(size_A4, aspectRatioMode=1)

            current_page = self.graphics.addPixmap(image_sized)
            current_page.setOffset(pos_TL)
            self.paper_list.append(current_page)

            page_TL = QPointF(x_left_px - margin_x_px, y_top_px - margin_y_px)
            page_BR = QPointF(x_left_px + A4_body_x_px + margin_x_px, y_top_px + A4_body_y_px + margin_y_px)

            page = self.graphics.addRect(QRectF(page_TL, page_BR))
            self.paper_list.append(page)








