#/usr/bin/env python

import pyglet
import math

from pyglet.window import key, mouse

from app.libs.json_map import Map


def get_decomposed_direction_using_slope(distance, slope):
    d2 = distance*distance
    a2 = slope*slope
    x = math.sqrt(d2/(1+a2))
    y = math.sqrt(a2*d2/(1+a2))
    return x, y


def get_point_in_direction(distance, start_position, point_in_direction, stop_at_target=False):
    if distance is None or start_position is None or point_in_direction is None:
        raise Exception("Foo Bar!")
    p = start_position
    q = point_in_direction
    x_diff = q[0]-p[0]
    if x_diff == 0:
        return point_in_direction
    slope = (q[1]-p[1])/x_diff
    rv_x, rv_y = get_decomposed_direction_using_slope(distance, slope)
    if p[0] > q[0]:
        rv_x *= -1
    if p[1] > q[1]:
        rv_y *= -1
    relative_vector = rv_x, rv_y
    new_point = start_position[0] + relative_vector[0], start_position[1] + relative_vector[1]
    if stop_at_target and abs(p[0]-q[0]) < abs(p[0]-new_point[0]):
        new_point = point_in_direction
    return new_point


class Animation():

    def __init__(self, resource, rows, columns, start_pos=(1, 1), start_rotation=0.0, speed=200):
        if rows < 1 or columns < 1:
            Exception("Animation initialized with zero-dimension.")
        self.bin = pyglet.image.atlas.TextureBin()
        self.spritesheet = pyglet.image.load(resource)
        self.image_grid = pyglet.image.ImageGrid(self.spritesheet, rows, columns)

        self.start_rotation = start_rotation
        self.number_of_rows = rows
        self.number_of_columns = columns
        self.speed = speed
        self.target_position = None
        self.current_angle = 0
        self.current_position = start_pos

        self.animations, self.sprites = self.setup_animation(self.image_grid, rows, columns, 0.25)
        self.current_animation = self.animations[0]
        self.sprite = self.sprites[0]

    def setup_animation(self, img_grid, num_rows, num_columns, period):
        sprites = []
        animations = []
        image_frames = []
        for i in range(0, num_rows * num_columns):
            frame_index = i
            frame = img_grid[frame_index]
            animation_frame = (pyglet.image.AnimationFrame(frame, period))
            image_frames.append(animation_frame)
            if frame_index % num_columns is 0:
                new_animation = pyglet.image.Animation(image_frames)
                animations.append(new_animation)
                sprites.append(pyglet.sprite.Sprite(new_animation))
                image_frames = []
        return animations, sprites

    def set_target_position(self, new_position):
        print("New target position: {0}".format(new_position))
        self.target_position = new_position

    def set_speed(self, new_speed):
        self.speed = new_speed

    def update(self, dt):
        distance = dt * self.speed
        movement = self.move(distance)
        self.update_sprite(movement)

    def get_animation_index(self):
        pi2 = 2 * math.pi
        angle = self.start_rotation + self.current_angle
        angle %= pi2
        return int(self.number_of_rows * angle / pi2)

    def update_sprite(self, movement):

        if abs(movement[0]) > 1 or abs(movement[1] > 1):
            animation_index = self.get_animation_index()
            self.sprite = self.sprites[animation_index]
            self.current_animation = self.animations[animation_index]
        else:
            self.sprite = pyglet.sprite.Sprite(self.current_animation)  # self.current_animation)

        x, y = self.current_position
        self.sprite.set_position(x-self.sprite.width/2, y-self.sprite.height/2)

    def set_position(self, new_position):
        # print("New animation position: {0} <<".format(new_position))
        self.current_position = new_position

    def move(self, distance):
        if self.target_position is None:
            return 0, 0

        new_position = get_point_in_direction(distance,
                                              self.current_position, self.target_position, stop_at_target=True)
        delta_x = new_position[0] - self.current_position[0]
        delta_y = new_position[1] - self.current_position[1]
        intended_delta_x = self.target_position[0] - self.current_position[0]
        intended_delta_y = self.target_position[1] - self.current_position[1]
        self.current_angle = math.atan2(intended_delta_y, intended_delta_x)
        self.set_position(new_position)
        return delta_x, delta_y

    def self_draw(self, batch=None):
        if self.sprite is not None:
            if batch is None:
                self.sprite.draw()
            else:
                batch.add(self.sprite)

    def draw(self, batch=None):
        self.self_draw(batch)







window = pyglet.window.Window(caption="PyThomas",
                              fullscreen=False,
                              resizable=False,
                              visible=False)

# load the map
fd = pyglet.resource.file("test.json", 'rt')
print("{0}".format(fd))
m = Map.load_json(fd)
animation = Animation("walk.png", 8, 8, start_rotation=-math.pi)

# set the viewport to the window dimensions
window.set_size(m.p_width, m.p_height)
m.set_viewport(0, 0, m.p_width, m.p_height)
window.set_visible(True)

window.set_size(400, 300)
window.set_size(m.p_width, m.p_height)


dims = [(m.p_width, m.p_height),
        (window.get_size()[0], window.get_size()[1]),
        (window.width, window.height)]
for dim in dims:
    print("{0},{1}".format(dim[0], dim[1]))


def update(dt):
    animation.update(dt)
pyglet.clock.schedule_interval(update, 0.1)


#
# # perform some queries to the map data!
#
# # list all the objects
# print("listing all the objects:")
# for obj in m.objectgroups["Objects"]:
#     print(obj)
#
# # is there a "Door1" object?
# print("Door1" in m.objectgroups["Objects"])
#
# # is there aan object in coords 10, 10?
# print((0, 10) in m.objectgroups["Objects"])
#
# # get the object named "Door1"
#print("Star1:", m.objectgroups["Objects"]["Star1"])
#
# # get the object in coords (5, 3)
# print("Obj at (5, 3)", m.objectgroups["Objects"][1, 17])
#
# # list all the objects with type "Door":
# print("listing all the Door objects:")
# for obj in m.objectgroups["Objects"].get_by_type("Star"):
#     print(obj)

print("---- ---- ----")
print("Thing: {0}".format(m.p_width))


@window.event
def on_draw():
    window.clear()
    m.set_viewport(0, 0, window.width, window.height)

    m.draw()
    batch = pyglet.graphics.Batch()
    animation.draw()

    def draw_rectangle(x, y, width, height):
        points = [x, y, x+width, y, x+width, y+height, x, y+height]
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', points))
    draw_rectangle(x=50, y=100, width=200, height=50)

    def draw_diagonal_rectangle(start_point, end_point, radius):
        x1 = start_point[0]
        y1 = start_point[1]
        x2 = end_point[0]
        y2 = end_point[1]
        slope = (y2-y1)/(x2-x1)

        tilt_dimensions = get_decomposed_direction_using_slope(radius, slope)

        # tilt_width = width/2 / slope_inv

        # points = [100, 100, 250, 250, 500, 400, 150, 300]
        # pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', points))
    draw_diagonal_rectangle((100, 100), (300, 300), 10)

    batch.draw()


@window.event
def on_resize(width, height):
    # if width < 300:
    #     width = 300
    # if height < 300:
    #     height = 300
    m.set_viewport(0, 0, width, height)
    # m.set_viewport(0, 0, window.width, window.height)


@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.F:
        window.set_fullscreen(window.fullscreen)
    if symbol == key.T:
        window.set_size(400, 300)
        window.set_size(m.p_width, m.p_height)
    if symbol == key.G:
        window.set_size(400, 300)


@window.event
def on_mouse_press(x, y, button, modifiers):
    clicked_pos = (x, y)
    if button == mouse.RIGHT:
        # animation.set_target_position(clicked_pos)
        animation.set_target_position(clicked_pos)
    pass


@window.event
def on_mouse_release(x, y, button, modifiers):
    pass


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    pass


pyglet.app.run()

