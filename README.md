# triq
Hackery to use trio async framework with PyQt

## Use at your own risk
The way this code uses Qt is explicitly discouraged by Qt developers.
Unfortunately, there seem to be no better way to marry trio event loop
with Qt event loop. If you know one, please let me know.

## How to
```python
...
import triq
import trio

async def some_async_func(message):
    await trio.sleep(0.5)
    print(message)

app = QApplication([])

hitme = QPushButton('Hit me')
hitme.clicked.connect(lambda: triq.call_async(some_async_func, 'hello, world!'))
hitme.show()

bye = QPushButton('Bye')
bye.clicked.connect(triq.exit)
bye.show()

triq.run(app)
```
