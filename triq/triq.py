import trio
from collections import deque

_tasks = deque()

_exit_event = trio.Event()

_TIMING = 0.005

def call_async(fn, *av):
    _tasks.append( (fn, av) )

def exit():
    _exit_event.set()

async def _main(app):
    async with trio.open_nursery() as nursery:
        while not _exit_event.is_set():
            app.processEvents()
            if _tasks:
                fn, args = _tasks.popleft()
                nursery.start_soon(fn, *args)
            else:
                with trio.move_on_after(_TIMING):
                    await _exit_event.wait()


def run(app):
    trio.run(_main, app)
    app.exit()
