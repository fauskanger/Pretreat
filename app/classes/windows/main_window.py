import math
import pyglet
from pyglet.window import key, mouse

from app.config import config
from app.pythomas import pythomas as lib
from app.classes.animation import Animation
from app.classes.navigation_graph import NavigationGraph, Node
from app.pythomas.pythomas import PygletLib as Plib


class BaseEventHandler:
    def __init__(self, window):
        self.window = window

    def on_key_press(self, symbol, modifiers):
        pass

    def on_key_release(self, symbol, modifiers):
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass


class BaseWindow:
    def __init__(self, window_name="Base Window", window_parameters=None):
        if window_parameters is None:
            window_parameters = BaseWindow.get_default_window_parameters()
        # super(BaseWindow, self).__init__(**window_parameters)
        self.window = pyglet.window.Window(**window_parameters)
        self.window_name = window_name
        self.pressed_keys = key.KeyStateHandler()
        self.window.push_handlers(self.pressed_keys)

    def update(self, dt):
        pass

    def run_update(self):
        pyglet.clock.schedule_interval(self.update, 1.0/config.window.desired_fps)

    @staticmethod
    def get_default_window_parameters():
        platform = pyglet.window.get_platform()
        display = platform.get_default_display()
        screen = display.get_default_screen()

        print('Display: {0}'.format(display))
        print('Screen: {0}'.format(screen))

        def get_initial_window_size():
            if config.window.fullscreen:
                display_scale = 1
            else:
                display_scale = config.window.default_fraction_of_screen

            width = int(config.window.default_width)
            height = int(config.window.default_height)
            if config.window.is_fraction_of_screen:
                width = int(screen.width*display_scale)
                height = int(screen.height*display_scale)
            return height, width
        window_height, window_width = get_initial_window_size()
        return dict(caption=config.strings.title,
                    fullscreen=config.window.fullscreen,
                    resizable=config.window.resizable,
                    width=window_width,
                    height=window_height,
                    visible=False)


class MainWindow(BaseWindow):
    def __init__(self):
        super(MainWindow, self).__init__("Main window")
        # self.push_handlers()
        self.nav_graph = NavigationGraph()
        # Create content
        self.text_label = pyglet.text.Label('Hello, world. Press F!',
                                            font_name='Times New Roman',
                                            font_size=self.window.height/10,
                                            x=self.window.width // 2, y=self.window.height // 2,
                                            anchor_x='center', anchor_y='center',
                                            color=(255, 0, 0, 255))
        self.background_image = pyglet.resource.image(lib.resource('bag/oasis2.png'))
        self.agent_image = pyglet.resource.image(lib.resource("walk.png"))
        self.animation = Animation(self.agent_image, 8, 8, start_rotation=-math.pi)
        self.window.set_visible(True)
        if not self.window.fullscreen:
            self.window.set_size(self.background_image.width, self.background_image.height)
        self.window.push_handlers(self)
        self.window.push_handlers(self.animation)
        # self.fit_label(self.text_label)

    def update(self, dt):
        self.animation.update(dt)

    def on_draw(self):
        self.window.clear()
        self.background_image.blit(0, 0)

        def draw_graph():
            nav_batch = pyglet.graphics.Batch()
            self.nav_graph.draw(nav_batch)
            nav_batch.draw()
        draw_graph()
        self.text_label.draw()
        self.animation.draw()
        # lib.PygletLib.draw_rectangle(x=50, y=100, width=200, height=50)
        # lib.PygletLib.draw_diagonal_rectangle((100, 100), (300, 300), 10)

    def on_key_press(self, symbol, modifiers):
        pass
        # text = 'A key was pressed'
        # if symbol == key.F:
        #     Plib.toggle_fullscreen(self)
        # if symbol == key.A and modifiers & key.LSHIFT:
        #     text = 'The "A+LSHIFT" key was pressed.'
        # elif symbol == key.LEFT:
        #     text = 'The left arrow key was pressed.'
        # elif symbol == key.ENTER:
        #     text = 'The enter key was pressed.'
        # self.text_label.text = text

    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            if Plib.is_ctrl_pressed(self.pressed_keys):
                self.nav_graph.add_node(Node(x, y))
        #     self.text_label.text = 'The left mouse button was pressed {0},{1}.'.format(x, y)
        if button == mouse.RIGHT:
            self.animation.set_target_position((x, y))
        # if button == mouse.MIDDLE:
        #     self.text_label.text = 'The middle mouse button was pressed {0},{1}.'.format(x, y)

    def on_resize(self, width, height):
        self.background_image.width = width
        self.background_image.height = height
        pass
