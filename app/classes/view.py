import pyglet

from app.config import config
from app.classes.windows.main_window import MainWindow
from app.classes.windows.test_window import TestWindow


class View():
    def __init__(self):
        if config.test:
            self.window = TestWindow()
        else:
            self.window = MainWindow()

    def run(self):
        print("Starting window: {0}".format(self.window.window_name))
        self.window.run_update()
        pyglet.app.run()