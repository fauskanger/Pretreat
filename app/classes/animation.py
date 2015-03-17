import pyglet
import math
from enum import Enum
from app.pythomas import pythomas as lib


class Animation():

    class State(Enum):
        Idle = 0,
        Move = 1

    def __init__(self, resource, rows, columns,
                 start_pos=(1, 1),
                 position_offset=(0.0, 0.0),
                 start_rotation=0.0,
                 speed=200):
        if rows < 1 or columns < 1:
            Exception("Animation initialized with negative or zero-dimension. ({0}x{1})"
                      .format(rows, columns))
        self.bin = pyglet.image.atlas.TextureBin()
        self.spritesheet = pyglet.image.load(resource)
        self.image_grid = pyglet.image.ImageGrid(self.spritesheet, rows, columns)

        self.position_offset = position_offset
        self.start_rotation = start_rotation
        self.number_of_rows = rows
        self.number_of_columns = columns
        self.speed = speed
        self.target_position = None
        self.current_angle = 0
        self.current_position = start_pos
        self.previous_move = None

        def setup_animation(img_grid, num_rows, num_columns, period):
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
        self.animations, self.sprites = setup_animation(self.image_grid, rows, columns, 0.25)
        self.current_animation = self.animations[0]
        self.sprite = self.sprites[0]


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
        new_position = new_position[0]+self.position_offset[0], new_position[1]+self.position_offset[1]
        self.current_position = new_position

    def get_previous_move(self):
        if self.previous_move is None:
            return 0, 0
        else:
            return self.previous_move

    def move(self, distance):
        if self.target_position is None:
            return 0, 0

        new_position = lib.get_point_in_direction(distance,
                                                  self.current_position,
                                                  self.target_position,
                                                  stop_at_target=True)
        self.set_position(new_position)

        def update_angle():
            target_dx, target_dy = self.get_relative_target_vector()
            return math.atan2(target_dy, target_dx)
        self.current_angle = update_angle()

        def calc_move_distance():
            delta_x = new_position[0] - self.current_position[0]
            delta_y = new_position[1] - self.current_position[1]
            return delta_x, delta_y
        self.previous_move = calc_move_distance()

        return self.get_previous_move()

    def get_relative_target_vector(self):
        x = self.target_position[0] - self.current_position[0]
        y = self.target_position[1] - self.current_position[1]
        return x, y



    def self_draw(self, batch=None):
        if self.sprite is not None:
            if batch is None:
                self.sprite.draw()
            else:
                batch.add(self.sprite)

    def draw(self, batch=None):
        self.self_draw(batch)

