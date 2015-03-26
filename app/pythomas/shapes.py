import math
import pyglet
from app.pythomas import pythomas as lib
from app.config import config


class Shape(object):
    def __init__(self, position, color=None, color_list=None, mode=pyglet.gl.GL_POLYGON):
        self.x = int(position[0])
        self.y = int(position[1])
        self.vertex_list = None
        self.draw_points_list = None  # self.create_draw_points()
        self.vertex_list = None  # self.create_vertex_list()
        self.translate = None
        self.color_list = color_list
        self.color = color
        if color is not None:
            self.color_list = None
        self.mode = mode

    def set_position(self, new_position, translate=True):
        # if translate:
        #     self.translate = new_position[0] - self.x, new_position[1] - self.y
        self.x = int(new_position[0])
        self.y = int(new_position[1])
        self.update_shape()

    def update_draw_points(self):
        self.draw_points_list = self.create_draw_points()

    def create_draw_points(self):
        return None

    def get_position(self):
        return self.x, self.y

    def set_color(self, color):
        self.color = color
        self.update_color_list()
        self.vertex_list.colors = self.color_list

    def update_vertex_list(self):
        if self.vertex_list is None:
            return False

    def update_color_list(self, number_of_vertices=None):
        if number_of_vertices is None:
            number_of_vertices = self.vertex_list.count
        count_needed = 3*number_of_vertices

        def get_diff():
            return len(self.color_list) - count_needed
        if self.color is not None:
            self.color_list = list(self.color*number_of_vertices)
        elif self.color_list is None:
            print("Warning: Updated color to red from default color.")
            self.color_list = list(lib.colors.red*number_of_vertices)
        elif self.color_list is not None and get_diff() != 0:
            while get_diff() > 0:
                self.color_list.remove(self.color_list[-3])
            while get_diff() < 0:
                self.color_list.append(self.color_list[:3])
        return self.color_list

    def create_vertex_list(self):
        # Create a vertex list from shape attributes
        if self.draw_points_list is None:
            return None
        number_of_vertices = int(len(self.draw_points_list)/2)
        self.update_color_list(number_of_vertices)
        vertex_list = pyglet.graphics.vertex_list(number_of_vertices, 'v2f', config.world.color_mode)
        vertex_list.vertices = self.draw_points_list
        vertex_list.colors = self.color_list
        return vertex_list

    def update_vertex_list_points(self):
        # if self.translate and self.vertex_list and self.vertex_list.vertices:
        #     for i in range(self.vertex_list.count):
        #         self.vertex_list.vertices[0 + i*2] += self.translate[0]
        #         self.vertex_list.vertices[1 + i*2] += self.translate[1]
        #         self.translate = None
        # else:
        self.vertex_list = self.create_vertex_list()

    def update_shape(self):
        # if not self.translate and not self.draw_points_list:
        self.update_draw_points()
        self.update_vertex_list_points()

    def draw(self, batch=None):
        # TODO: Fix batched draw
        batch = None
        if self.vertex_list is None:
            return
        if batch is None:
            # pyglet.graphics.draw(self.vertex_list.get_size(), mode, self.vertex_list)
            self.vertex_list.draw(self.mode)
        else:
            batch.add(self.vertex_list.get_size(), self.mode, None,
                      ('v2f', self.vertex_list.vertices),
                      (config.world.color_mode, self.vertex_list.colors))


class Circle(Shape):
    def __init__(self, position, radius, color):
        Shape.__init__(self, position, color, mode=pyglet.gl.GL_TRIANGLE_FAN)
        self.radius = radius
        self.update_shape()

    def create_draw_points(self):
        return lib.get_circle_points(center=(self.x, self.y), radius=self.radius, include_center=True)

    def set_radius(self, radius):
        if radius >= 0.0 and radius != self.radius:
            self.radius = radius
            self.update_shape()

    def expand_radius(self, value):
        if -value < self.radius and value != 0.0:
            self.set_radius(self.radius+value)


class Rectangle(Shape):
    def __init__(self, start_point, end_point, radius, colors_list=None, color=None):
        Shape.__init__(self, position=lib.get_middle(start_point, end_point),
                       color=color, color_list=colors_list, mode=pyglet.gl.GL_QUADS)
        x1 = start_point[0]
        y1 = start_point[1]
        x2 = end_point[0]
        y2 = end_point[1]

        a = abs(x2-x1)
        b = abs(y2-y1)
        self.start_point = start_point
        self.end_point = end_point
        self.width = math.sqrt(a*a + b*b)
        self.height = radius
        # if color is not None:
        #     self.color_list = list(color * 4)
        # elif colors_list is None:
        #     colors_list = list(colors.white)
        # self.colors_list = colors_list
        self.update_shape()

    def create_draw_points(self):
        # center = get_middle(start_point, end_point)
        rectangle_points = lib.get_rectangle_on_point(self.get_position(), self.width, self.height)
        x1 = self.start_point[0]
        y1 = self.start_point[1]
        x2 = self.end_point[0]
        y2 = self.end_point[1]
        theta = math.atan2(y2-y1, x2-x1)
        rotated_rectangle_points = []
        self_position = self.get_position()
        for p in rectangle_points:
            rotated_p = lib.rotate_point_around_point(p, self_position, theta)
            rotated_rectangle_points.extend(rotated_p)
        return rotated_rectangle_points