from app.config import config
from app.classes.views import PygletWindowView
from app.classes.views import ConsoleView


class Main:
    def __init__(self):
        self.title = config.strings.title
        self.view = None

    def run(self):
        window = False
        if window:
            self.view = PygletWindowView()
        else:
            self.view = ConsoleView()
        self.view.run()

app = Main()
