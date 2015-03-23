import numpy as np
import math
from app.config import config, Colors


def for_each_node_in(graph, lambda_method, is_reading_data=False):
    for node in graph.nodes(data=is_reading_data):
        if is_reading_data:
            node = node[0]
        lambda_method(node)


def get_circle_points(center=(0.0, 0.0), radius=1.0, number_of_points=32, include_center=False, repeat=True):
    points_list = []
    for i in range(number_of_points):
        a = 2.0*math.pi*float(i)/number_of_points
        points_list.append(center[0]+radius*math.sin(a))
        points_list.append(center[1]+radius*math.cos(a))
    if include_center and repeat:
        points_list.append(points_list[0])
        points_list.append(points_list[1])
    if include_center:
        points_list.insert(0, center[0])
        points_list.insert(1, center[1])
    return points_list


def flatten_list_of_tuples(list_of_tuples):
    value_list = []
    for t in list_of_tuples:
        value_list.extend(t)
    return value_list


def resource(filename):
    path = '{0}/{1}'.format(config.strings.resource_path, filename)
    print("Resource path concat: {0}".format(path))
    return path


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
    # Added for readability, the vector is the equivalent of solving the problem at origo
    relative_vector = rv_x, rv_y
    new_point = start_position[0] + relative_vector[0], start_position[1] + relative_vector[1]
    if stop_at_target and abs(p[0]-q[0]) < abs(p[0]-new_point[0]):
        new_point = point_in_direction
    return new_point


def get_rectangle_on_point(point, width, height):
    x, y = point[0], point[1]
    p1 = x-width/2, y+height/2
    p2 = x-width/2, y-height/2
    p3 = x+width/2, y-height/2
    p4 = x+width/2, y+height/2
    return [p1, p2, p3, p4]


def get_rotation_matrix(theta):
    return np.array([[math.cos(theta), -math.sin(theta)],
                    [math.sin(theta),  math.cos(theta)]])


def rotate_point_around_point(point, axis_point, radians_theta):
    theta = radians_theta
    x, y = point[0], point[1]
    cx, cy = axis_point[0], axis_point[1]
    point_vector = np.reshape([x, y], 2, 1)
    translation_matrix = np.reshape([cx, cy], 2, 1)
    rotation_matrix = get_rotation_matrix(theta)

    center_vector = np.subtract(point_vector, translation_matrix)
    rotated_center_vector = np.dot(rotation_matrix, center_vector)
    rotated_vector = np.add(rotated_center_vector, translation_matrix)
    x_new, y_new = rotated_vector[0], rotated_vector[1]

    return x_new, y_new


def get_point_distance(from_point, to_point):
    x = abs(from_point[0]-to_point[0])
    y = abs(from_point[1]-to_point[1])
    return math.sqrt(x*x + y*y)


def get_middle(point_a, point_b):
    x = (point_a[0]+point_b[0])/2
    y = (point_a[1]+point_b[1])/2
    return x, y


def sum_points(p, q):
    return p[0]+q[0], p[1]+q[1]

colors = Colors()


import pyglet
from pyglet.window import key


class Shape(object):
    def __init__(self, position, color=colors.white, mode=pyglet.gl.GL_POLYGON):
        self.x = int(position[0])
        self.y = int(position[1])
        self.vertex_list = None
        self.draw_points_list = None  # self.create_draw_points()
        self.vertex_list = None  # self.create_vertex_list()
        self.color = color
        self.mode = mode

    def set_position(self, new_position):
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

    def create_vertex_list(self):
        if self.draw_points_list is None:
            return None
        number_of_vertices = int(len(self.draw_points_list)/2)
        vertex_list = pyglet.graphics.vertex_list(number_of_vertices, 'v2f', config.world.color_mode)
        vertex_list.vertices = self.draw_points_list
        vertex_list.colors = self.color*number_of_vertices
        return vertex_list

    def update_vertex_list_points(self):
        self.vertex_list = self.create_vertex_list()

    def update_shape(self):
        self.update_draw_points()
        self.update_vertex_list_points()

    def draw(self, batch=None):
        if self.vertex_list is None:
            return
        if self.vertex_list is None:
            self.update_vertex_list_points()
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
        return get_circle_points(center=(self.x, self.y), radius=self.radius, include_center=True)

    def set_radius(self, radius):
        if radius >= 0.0 and radius != self.radius:
            self.radius = radius
            self.update_shape()

    def expand_radius(self, value):
        if -value < self.radius and value != 0.0:
            self.set_radius(self.radius+value)


class Rectangle(Shape):
    def __init__(self, start_point, end_point, radius, colors_list=None):
        Shape.__init__(self, get_middle(start_point, end_point), mode=pyglet.gl.GL_QUADS)
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
        if colors_list is None:
            color = [(255, 255, 255) * 4]
            colors_list = flatten_list_of_tuples(color)
        self.colors_list = colors_list
        self.update_shape()

    def create_draw_points(self):
        # center = get_middle(start_point, end_point)
        rectangle_points = get_rectangle_on_point(self.get_position(), self.width, self.height)
        x1 = self.start_point[0]
        y1 = self.start_point[1]
        x2 = self.end_point[0]
        y2 = self.end_point[1]
        theta = math.atan2(y2-y1, x2-x1)
        rotated_rectangle_points = []
        for p in rectangle_points:
            rotated_p = rotate_point_around_point(p, self.get_position(), theta)
            rotated_rectangle_points.extend(rotated_p)
        return rotated_rectangle_points


# pyglet-specific library
class PygletLib:



    @staticmethod
    def is_shift(modifiers):
        return modifiers & (key.LSHIFT | key.RSHIFT)

    @staticmethod
    def is_shift_pressed(pressed_keys):
        return pressed_keys[key.LSHIFT] or pressed_keys[key.RSHIFT]

    @staticmethod
    def is_ctrl(modifiers):
        return modifiers & (key.LCTRL | key.RCTRL)

    @staticmethod
    def is_ctrl_pressed(pressed_keys):
        return pressed_keys[key.LCTRL] or pressed_keys[key.RCTRL]

    @staticmethod
    def is_alt(modifiers):
        return modifiers & (key.LALT | key.RALT)

    @staticmethod
    def is_alt_pressed(pressed_keys):
        return pressed_keys[key.LALT] or pressed_keys[key.RALT]

    @staticmethod
    def toggle_fullscreen(window):
        window.set_fullscreen(not window.fullscreen)

    @staticmethod
    def draw_rectangle(x, y, width, height):
        points = []
        p1 = x, y
        p2 = x+width, y
        p3 = x+width, y+height
        p4 = x, y+height
        tuple_list = [p1, p2, p3, p4]
        for coordinate in tuple_list:
            points.extend(coordinate)
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', points))

    # @staticmethod
    # def draw_diagonal_rectangle(start_point, end_point, radius, colors_list=None):
    #     x1 = start_point[0]
    #     y1 = start_point[1]
    #     x2 = end_point[0]
    #     y2 = end_point[1]
    #
    #     a = abs(x2-x1)
    #     b = abs(y2-y1)
    #     width = math.sqrt(a*a + b*b)
    #     height = radius
    #     if colors_list is None:
    #         color = [(255, 255, 255) * 4]
    #         colors_list = flatten_list_of_tuples(color)
    #
    #     center = get_middle(start_point, end_point)
    #     rectangle_points = get_rectangle_on_point(center, width, height)
    #     theta = math.atan2(y2-y1, x2-x1)
    #     rotated_rectangle_points = []
    #     for p in rectangle_points:
    #         rotated_p = rotate_point_around_point(p, center, theta)
    #         rotated_rectangle_points.extend(rotated_p)
    #     pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', rotated_rectangle_points), ('c3B', colors_list))
