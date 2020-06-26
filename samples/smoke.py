'''
Demonstrates how to run asynchronous jobs from Qt application.
'''
import triq
import trio
try:
    from PyQt5.QtWidgets import QApplication, QPushButton
except:
    from PySide2.QtWidgets import QApplication, QPushButton

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
