import pyglet
from app.classes.windows.main_window import MainWindow


class View():
    def __init__(self):
        self.window = MainWindow()

    def run(self):
        print("Starting app: {0}".format(self.window.window_name))
        self.window.run_update()
        pyglet.app.run()