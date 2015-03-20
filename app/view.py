import math
import pyglet
from pyglet.window import key, mouse
from app.classes.windows.main_window import MainWindow, BaseWindow
from app.config import config
from app.pythomas import pythomas as lib


class View():
    def __init__(self):
        self.window = MainWindow()

    def run(self):
        print("Starting app: {0}".format(self.window.window_name))
        self.window.run_update()
        pyglet.app.run()