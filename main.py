import sys
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QGraphicsScene
from ui_generated import Ui_MainWindow
import logging
from rasterer import Rasterer

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

        self.rasterer = Rasterer(self)

    def confirmUI(self, ui_widgets):
        print("confirming ui")
        self.widgets = ui_widgets
        self.rasterer.confirm_UI(ui_widgets)

    def resizeEvent(self, *args, **kwargs):
        super().resizeEvent(*args, **kwargs)
        print("resize event")
        self.rasterer.handle_resizing()


if __name__ == "__main__":
    monitor_width = 1920
    monitor_height = 1080

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MyUI()
    ui = Ui_MainWindow()

    ui.setupUi(MainWindow)
    MainWindow.confirmUI(ui)
    #MainWindow.set_image(image_location)
    MainWindow.setWindowIcon(QIcon("icon.ico"))

    MainWindow.show()
    sys.exit(app.exec_())