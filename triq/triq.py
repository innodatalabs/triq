'''
Ideas how to use trio guest mode with Qt borrowed from:

https://github.com/altendky/alqtendpy/pull/19/files
'''
import trio
import traceback


_MAX_CONCURRENT_TASKS = 100
_send_channel, _receive_channel = trio.open_memory_channel(_MAX_CONCURRENT_TASKS)

_EXIT = object()


def exit():
    _send_channel.send_nowait(_EXIT)


def call_async(fn, *av):
    _send_channel.send_nowait( (fn, av) )

def default_exception_handler(err):
    traceback.print_exception(type(err), err, err.__traceback__)

def run(app, reenter=None):
    if reenter is None:
        from .qt import Reenter
        reenter = Reenter()
    _reenter = reenter

    async def run_task(fn, *av):
        try:
            await fn(*av)
        except Exception as err:
            raise err
            _exception_handler(err)

    async def _main():
        async with trio.open_nursery() as nursery:
            app.lastWindowClosed.connect(nursery.cancel_scope.cancel)
            async for x in _receive_channel:
                if x is _EXIT:
                    break
                fn, av = x
                nursery.start_soon(run_task, fn, *av)

    def _done(trio_main_outcome):
        trio_main_outcome.unwrap()
        app.quit()

    def _schedule(callable_):
        app.postEvent(_reenter, _reenter.createEvent(callable_))

    trio.lowlevel.start_guest_run(
        _main,
        run_sync_soon_threadsafe=_schedule,
        done_callback=_done,
    )

    return app.exec_()
