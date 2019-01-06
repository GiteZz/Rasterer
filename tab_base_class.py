from abc import ABCMeta, abstractmethod

class TabBaseClass(object):
    __metaclass__ = ABCMeta
    def __init__(self, parent):
        pass

    @abstractmethod
    def confirmUI(self, widgets):
        pass

    @abstractmethod
    def tab_changed(self):
        pass