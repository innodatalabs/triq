try:
    from PyQt5.QtCore import QEvent, QObject
except ImportError:
    from PySide2.QtCore import QEvent, QObject


class ReenterEvent(QEvent):
    REENTER_EVENT = QEvent.Type(QEvent.registerEventType())

    def __init__(self, fn):
        self._fn = fn
        super().__init__(self.REENTER_EVENT)

    def consume(self):
        self._fn()
        return False

class Reenter(QObject):
    def event(self, event):
        return event.consume()

    @classmethod
    def createEvent(cls, fn):
        return ReenterEvent(fn)
