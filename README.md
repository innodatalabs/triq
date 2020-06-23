# triq
Use [trio](https://github.com/python-trio/trio) async framework
with PyQt5/PySide2

## Caution
This is an alpha-quality software.

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

The above should work in PyQt5 and PySide2
