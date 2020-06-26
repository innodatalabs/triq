'''
Demonstrates running asynchronous tasks with progress bar and Abort button,
handling of errors.

ProgressDialog: a modal dialog with progress bar and Abort button, handles errors
    by displaying them in a message box
ProgressBar: a widget, suitale for embedding into layout and showing progress bar.
    No way to abort execution
NullProgress: a do-nothing progress object, suitable for testing code that
    uses progress api.
PrintProgress: a simple printing progress implementation, good for non-GUI
    applications (e.g. CLI)

Progress API:
function that wants to report progress to the user, must:
1. be async
2. accept a keyword argument named "progress"
3. in its body do this:
    ```
    async def my_worker(progress=NullProgress):
        with progress(title='My worker working', ticks=200):
            # do something
            progress.tick(label='reading stream')  # report progress periodically
            ...
            # call subroutines, passing progress down
            await my_other_code(progress=progress)
    ```

ProgressDialog will display modal progress dialog, showing the progress. When finished,
progress dialog will disappear.

Other implementations of progress are possible, as required by your UI design.
'''
import contextlib
import time
import trio
import sys
try:
    from PyQt5.QtWidgets import QProgressDialog, QMessageBox, QApplication, QPushButton
    from PyQt5.QtCore import Qt
except ImportError:
    from PySide2.QtWidgets import QProgressDialog, QMessageBox, QApplication, QPushButton
    from PySide2.QtCore import Qt


@contextlib.contextmanager
def connect(source, target):
    try:
        source.connect(target)
        yield
    finally:
        source.disconnect(target)


class _ThrottlingProgressProxy:
    def __init__(self, engine):
        self._engine = engine
        self._lastTick = time.time()
        self._value = engine.value()
        self._maximum = engine.maximum()
        self._label = None

    def tick(self, advance=1, label=None):
        self._value += 2 * advance
        self._maximum += 2 * advance
        if label is not None:
            self._label = label
        now = time.time()
        if now > self._lastTick + 0.1:
            self._lastTick = now
            self._engine.setValue(self._value)
            self._engine.setMaximum(self._maximum)
            if self._label is not None:
                self._engine.setLabelText(label)


class ProgressDialog:
    '''Displays visual progress bar featuring:
    * current tick label
    * percentage
    * Abort button to cancel the run
    * Exceptions displayed

    Use it to run asynchronous tasks in a modal way
    '''

    def __init__(self, parent):
        '''Creates an instance. To actually show the dialog use context manager.

        Args:
            parent (Qt Widget): parent component for the dialog
        '''
        self._parent = parent
        self._level = 0
        self._ui = None
        self._throttler = None

    @contextlib.asynccontextmanager
    async def __call__(self, title='Please wait', ticks=100):
        '''Shows the dialog and creates a context for "ticking".

        Args:
            title (str): dialof window title, default "Please wait"
            ticks (int): total number of expected ticks (can be approximate). Establishes
                the "scale" of the progress bar.

        Withing this context one can use :meth:`tick()` to advance the progress and
        change tick label.
        '''
        if ticks <= 0:
            raise ValueError('units should be positive')

        if self._level > 0:
            # allow passing progress object on to the sub-routines
            yield self
            return

        self._ui = QProgressDialog(title, 'Abort', 0, ticks, self._parent)
        self._ui.setWindowModality(Qt.WindowModality.WindowModal)
        self._ui.setMinimumDuration(500)
        self._throttler = _ThrottlingProgressProxy(self._ui)

        with trio.CancelScope() as cancel_scope:
            try:
                self._level += 1
                with connect(self._ui.canceled, cancel_scope.cancel):
                    yield
            except (Exception, trio.Cancelled) as err:
                self._ui.hide()
                message = str(err)
                if sys.exc_info()[0] != None:
                    import traceback
                    stack = traceback.format_exc(10)
                    if stack:
                        message += '\n' + stack

                QMessageBox.critical(self._parent, 'Error', message)
            finally:
                self._level -= 1

                self._ui.setValue(self._ui.maximum())
                self._ui.hide()
                self._ui.destroy()
                self._ui = None

    def tick(self, advance=1, label=None):
        '''Communicates that some progress was done with the task.

        Args:
            advance (int): how many tick units were completed (default is 1)
            label (str): optionally set the label of the "current work" to display
                in the ProgressDialog window.
        '''
        if self._level == 0:
            raise RuntimeError('Progress context is missing. Did you forger to do "async with progress()"?')

        self._throttler.tick(advance, label)


class NullProgress:
    @contextlib.asynccontextmanager
    async def __call__(self, title='Please wait', ticks=100):
        yield

    def tick(self, advance=1, label=None):
        pass

NullProgress.instance = NullProgress()


class PrintProgress:
    @contextlib.asynccontextmanager
    async def __call__(self, title='Please wait', ticks=100):
        print(title)
        yield

    def tick(self, advance=1, label=None):
        if label is None:
            print('.')
        else:
            print(label)

PrintProgress.instance = PrintProgress()

class ProgressBar:
    def __init__(self, bar):
        self._bar = bar
        self._level = 0
        self._throttler = None

    @contextlib.asynccontextmanager
    async def __call__(self, title='Please wait', ticks=100):
        if ticks <= 0:
            raise ValueError('ticks value must be positive')

        if self._level > 0:
            yield self
            return

        self._bar.setValue(0)
        self._bar.setMinimum(0)
        self._bar.setMaximum(ticks)
        self._throttler = _ThrottlingProgressProxy(self._bar)

        try:
            self._level += 1
            yield
        finally:
            self._level -= 1
            self._bar.setMaximum(self._maximum)
            self._bar.setValue(self._maximum)
            self._throttler = None

    def tick(self, advance=1, label=None):
        if self._level == 0:
            raise RuntimeError('Progress context is missing. Did you forger to do "async with progress()"?')

        self._throttler.tick(advance)  # no label here!


if __name__ == '__main__':
    import triq

    async def worker(progress=NullProgress.instance):
        async with progress(title='Hello', ticks=100):
            for y in range(10):
                await trio.sleep(0.1)
                progress.tick(label=f'{y}')
                await subroutine(y, progress)

    async def subroutine(y, progress=NullProgress.instance):
        async with progress(title='Something'):
            for x in range(10):
                await trio.sleep(0.1)
                progress.tick(label=f'{y}/{x}')

    app = QApplication([])

    widget = QPushButton('Start')
    progress = ProgressDialog(widget)
    # progress = PrintProgress()

    widget.clicked.connect(lambda: triq.call_async(worker, progress))

    widget.show()

    triq.run(app)
