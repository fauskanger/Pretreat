import numpy as np
import math
from app.config import config


# pyglet-specific library
class PygletLib:
    @staticmethod
    def is_shift(modifiers):
        return modifiers & (key.LSHIFT | key.RSHIFT)

    @staticmethod
    def is_ctrl(modifiers):
        return modifiers & (key.LCTRL | key.RCTRL)

    @staticmethod
    def is_alt(modifiers):
        return modifiers & (key.LALT | key.RALT)

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

    @staticmethod
    def draw_diagonal_rectangle(start_point, end_point, radius):
        x1 = start_point[0]
        y1 = start_point[1]
        x2 = end_point[0]
        y2 = end_point[1]

        a = abs(x2-x1)
        b = abs(y2-y1)
        width = math.sqrt(a*a + b*b)
        height = radius
        colors = [ (255, 000, 000),
                   (255, 000, 000),
                   (000, 255, 000),
                   (000, 255, 000), ]
        colors_list = flatten_list_of_tuples(colors)

        center = get_middle(start_point, end_point)
        rectangle_points = get_rectangle_on_point(center, width, height)
        theta = math.atan2(y2-y1, x2-x1)
        rotated_rectangle_points = []
        for p in rectangle_points:
            rotated_p = rotate_point_around_point(p, center, theta)
            rotated_rectangle_points.extend(rotated_p)
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', rotated_rectangle_points), ('c3B', colors_list))


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


def get_middle(point_a, point_b):
    x = point_a[0] + (point_a[0]-point_a[1])/2
    y = point_b[0] + (point_b[0]-point_b[1])/2
    return x, y

import pyglet
from pyglet.window import key


class PyThomas():

    @staticmethod
    def for_each_node_in(graph, lambda_method, is_reading_data=False):
        for node in graph.nodes(data=is_reading_data):
            if is_reading_data:
                node = node[0]
            lambda_method(node)

pythomas = PyThomas()