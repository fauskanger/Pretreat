import pyglet
from pyglet.window import key

from app.config import config


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

    def __init__(self, window_name, outer_handler=None, window_parameters=None):
        if window_parameters is None:
            window_parameters = BaseWindow.get_default_window_parameters()
        # super(BaseWindow, self).__init__(**window_parameters)
        self.window = pyglet.window.Window(**window_parameters)
        self.window_name = window_name
        self.outer_handler = outer_handler
        if self.outer_handler:
            self.window.push_handlers(self.outer_handler)
        self.pressed_keys = key.KeyStateHandler()
        self.window.push_handlers(self.pressed_keys)
        self.window.push_handlers(self)

    def run_update(self):
        pyglet.clock.schedule_interval(self.update, 1.0/config.window.desired_fps)
        if not self.window.visible:
            self.window.set_visible(visible=True)

    @staticmethod
    def get_default_window_parameters():
        platform = pyglet.window.get_platform()
        display = platform.get_default_display()
        screen = display.get_default_screen()

        template = pyglet.gl.Config(sample_buffers=1, samples=config.window.aa_samples)
        aa = "No"
        try:
            gl_config = screen.get_best_config(template)
        except pyglet.window.NoSuchConfigException:
            template = pyglet.gl.Config()
            gl_config = screen.get_best_config(template)
        else:
            aa = "Yes ({0}x{0})".format(gl_config.samples)

        # print('Display: {0}'.format(display))
        print('Screen: {0}'.format(screen))
        print('Anti-alias: {0}'.format(aa))

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
                    visible=False,
                    config=gl_config,
                    )

    def update(self, dt):
        pass

    def on_key_release(self, symbol, modifiers):
        pass

    def on_key_press(self, symbol, modifiers):
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_resize(self, width, height):
        pass

    def on_draw(self):
        pass