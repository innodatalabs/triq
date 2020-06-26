import asyncio
from unittest import mock
import traceback
import triq


_EXIT = object()

class MockApp:
    '''Mock Qt App using asyncio event loop.

    Inspired by: https://github.com/python-trio/trio/blob/eadb499336f7c068430f78b2e69b3d92e3cb8f02/trio/_core/tests/test_guest_mode.py#L319
    '''
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.queue = asyncio.Queue()

    def postEvent(self, object, event):
        def wrapper():
            try:
                event.consume()
            except Exception as err:
                self.queue.put_nowait(err)
        self.loop.call_soon_threadsafe(wrapper)

    def exec_(self):
        try:
            res = self.loop.run_until_complete(self.queue.get())
            if res is not _EXIT:
                raise res
        finally:
            self.loop.close()

    def quit(self):
        self.queue.put_nowait(_EXIT)

    lastWindowClosed = mock.Mock()


class MockReenterEvent:
    def __init__(self, fn):
        self._fn = fn

    def consume(self):
        self._fn()
        return False

class MockReenter:
    def event(self, event):
        return event.consume()

    @classmethod
    def createEvent(cls, fn):
        return MockReenterEvent(fn)
