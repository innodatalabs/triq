import trio
import time
import pytest
from triq.test.mock_qt import MockApp
import triq


def test_parallel_execution():
    '''Make sure paralell tasks are executed in paralell indeed'''

    report_work_done_here = []
    async def worker():
        await trio.sleep(5)
        report_work_done_here.append(time.time())

    app = MockApp()
    triq.call_async(worker)
    triq.call_async(worker)
    triq.exit()
    triq.run(app)

    assert len(report_work_done_here) == 2
    assert abs(report_work_done_here[0] - report_work_done_here[1]) < 1.0


def test_two_separate_tasks():
    '''Simple communication between two async tasks'''

    send_channel, receive_channel = trio.open_memory_channel(2)

    async def task1():
        await send_channel.send(1)

    async def task2():
        await send_channel.send(2)

    async def task3():
        result = set()
        result.add(await receive_channel.receive())
        result.add(await receive_channel.receive())
        assert result == {1, 2}

    app = MockApp()
    triq.call_async(task1)
    triq.call_async(task3)
    triq.call_async(task2)
    triq.exit()
    triq.run(app)
