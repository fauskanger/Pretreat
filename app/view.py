import math
import pyglet
from pyglet.window import key, mouse
from app.config import config
from app.pythomas import pythomas as lib


class View():
    def __init__(self):
        platform = pyglet.window.get_platform()
        display = platform.get_default_display()
        self.screen = screen = display.get_default_screen()

        print('Display: {0}'.format(display))
        print('Screen: {0}'.format(screen))

        def start_window():
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
            return pyglet.window.Window(caption=config.strings.title,
                                        fullscreen=config.window.fullscreen,
                                        resizable=config.window.resizable,
                                        width=window_width,
                                        height=window_height
                                        )
        self.window = window = start_window()

        # Create content
        self.label = label = pyglet.text.Label('Hello, world. Press F!', font_name='Times New Roman',
                                               font_size=window.height/10,
                                               x=window.width // 2, y=window.height // 2,
                                               anchor_x='center', anchor_y='center')
        self.image = image = pyglet.resource.image(lib.resource('cat.jpeg'))

        self.modifiers = 0


        def set_icons():
            icons = []
            for size in [16, 32, 64, 128]:
                icon_path = lib.resource('{0}/{1}.png'.format(config.strings.icon_folder, size))
                icon = pyglet.image.load(icon_path)
                icons.append(icon)
            window.set_icon(*icons)
            print(icons)
        set_icons()
        # window.push_handlers(pyglet.window.event.WindowEventLogger())

        # Set up event handlers
        @self.window.event
        def on_draw():
            window.clear()
            image.blit(0, 0)
            label.draw()

        @self.window.event
        def on_key_press(symbol, modifiers):
            text = 'A key was pressed'
            if symbol == key.F:
                self.toggle_fullscreen()
            if symbol == key.A and modifiers & key.LSHIFT:
                text = 'The "A+LSHIFT" key was pressed.'
            elif symbol == key.LEFT:
                text = 'The left arrow key was pressed.'
            elif symbol == key.ENTER:
                text = 'The enter key was pressed.'
            label.text = text

        @window.event
        def on_mouse_press(x, y, button, modifiers):
            if button == mouse.LEFT:
                label.text = 'The left mouse button was pressed {0},{1}.'.format(x, y)
            if button == mouse.RIGHT:
                label.text = 'The right mouse button was pressed {0},{1}.'.format(x, y)
            if button == mouse.MIDDLE:
                label.text = 'The middle mouse button was pressed {0},{1}.'.format(x, y)

        @window.event
        def on_resize(width, height):
            self.fit_label(width, height)
    #
    #   END __init__
    #

    def is_shift(self, modifiers):
        return modifiers & (key.LSHIFT | key.RSHIFT)

    def is_ctrl(self, modifiers):
        return modifiers & (key.LCTRL | key.RCTRL)

    def is_alt(self, modifiers):
        return modifiers & (key.LALT | key.RALT)

    def fit_label(self, width=None, height=None):
        if width is None:
            width = self.window.width
        if height is None:
            width = self.window.height
        target_width = width * 0.9
        target_height = height * 0.5

        def update_label_position():
            self.label.begin_update()
            width_ratio = target_width / self.label.content_width
            height_ratio = target_height / self.label.content_height
            if width_ratio < height_ratio:
                self.label.font_size *= width_ratio
            else:
                self.label.font_size *= height_ratio
            self.label.x, self.label.y = map(lambda x: 1 if x < 1 else x/2, [width, height])
            self.label.end_update()
        update_label_position()

    def toggle_fullscreen(self):
        window = self.window
        window.set_fullscreen(not window.fullscreen)

    def run(self):
        pyglet.app.run()