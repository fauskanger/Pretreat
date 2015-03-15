from app.config import config
from app.view import View


class Main():
    def __init__(self):
        print("Main started.")
        self.title = config.strings.title
        self.view = None

    def run(self):
        print("Running application: {0}".format(self.title))
        self.view = View()
        self.view.run()

app = Main()
