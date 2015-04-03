import numpy as np
import sqlite3
import math

from app.config import config, Colors


def db_connection():
    return sqlite3.connect(resource(config.strings.sqlite3_filename))


def try_remove(the_list, element):
    if not element:
        return False
    try:
        the_list.remove(element)
        return True
    except ValueError:
        return False


def try_append(the_list, element):
    if element is None:
        return False
    try:
        the_list.append(element)
        return True
    except ValueError:
        return False


def for_each_node_in(graph, lambda_method, is_reading_data=False):
    for node in graph.nodes(data=is_reading_data):
        if is_reading_data:
            node = node[0]
        lambda_method(node)


def bt709_y(rgb_color, rgb_range=255):
    # used to normalize output in range [0, 1]
    m = rgb_range
    r, g, b = rgb_color
    return 0.2126*r/m + 0.7152*g/m + 0.0722*b/m


def rgba(rgb, alpha=255):
    r, g, b = rgb
    return r, b, g, alpha


def interpolate_point(from_point, to_point, fraction):  # fraction is float in range [0, 1]
    x1, y1 = from_point
    x2, y2 = to_point
    x = fraction * (x2-x1) + x1
    a = (y2-y1)/(x2-x1)
    y = a*(x - x1) + y1
    return x, y


def get_circle_points(center=(0.0, 0.0), radius=10.0, number_of_points=32, include_center=False, repeat=True):
    points_list = []
    for i in range(number_of_points):
        a = 2.0*math.pi*float(i)/number_of_points
        points_list.append(center[0]+radius*math.cos(a))
        points_list.append(center[1]+radius*math.sin(a))
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


def get_closest_point(point, candidates):
    closest = None
    for candidate in candidates:
            if closest is None or get_point_distance(point, candidate) < get_point_distance(point, closest):
                closest = candidate
    return closest


def get_abc_roots(a, b, c, threshold=0.1):
    b2 = b*b
    ac4 = 4*a*c
    if b2 < ac4:
        return None
    elif abs(b2 - ac4) < threshold:
        return -b/(2*a),
    else:
        root = math.sqrt(b2-ac4)
        xs1 = (-b+root)/(2*a)
        xs2 = (-b-root)/(2*a)
        return xs1, xs2

    #   Intersection between line and circle:
    #
    # Solve y=slope(x-x1)+y1 and (x-xc)^2+(y-yc)^2=r^2
    #   y=slope(x-x1)+y1
    #   y=slope*x-slope*x1+y1
    # Use p = -slope*x1 + y1
    #   =>   y = slope*x + p
    # Replace y
    #   =>   (x-xc)^2+(slope*x + p - yc)^2=r^2
    # Use q = p - yc
    #   =>   (x-xc)^2+(slope*x + q)^2=r^2
    # Use sx = slope*x
    #   =>   (x-xc)^2+(sx + q)^2=r^2
    #   (x*x - 2*x*xc + xc*xc)  + (sx*sx + 2*sx*q + q*q) = r^2
    #   x*x+sx*sx - 2*x*xc + 2*sx*q + xc*xc + q*q - r*r = 0
    # Substitute sx
    #   =>   x*x*(1+slope*slope) + x*(-2*xc+2*slope*q) + (xc*xc+q*q-r*r) = 0
    # ABC for roots:
    #       a = slope*slope + 1
    #       b = -2*xc + 2*slope*q
    #       c = xc*xc + q*q - r*r


def get_point_on_circle(circle_center, radius, line_point, direction_point):
    xc, yc = circle_center
    x1, y1 = line_point
    xd, yd = direction_point
    r = radius
    slope = (yd-y1)/(xd-x1) if xd-x1 != 0 else None

    if slope is None:
        # Vertical line:
        # y = yc +/- root{r^2 - (x-xc)^2}
        root = math.sqrt(r*r - (x1 - xc)*(x1 - xc))
        ys1 = yc + root
        ys2 = yc - root
        p1 = x1, ys1
        p2 = x1, ys2
        return get_closest_point(direction_point, candidates=[p1, p2])

    def f(x):
        return slope*(x - x1) + y1

    def get_solution():
        def get_roots():
            p = -slope*x1 + y1
            q = p - yc

            # ax^2 + bx - c = 0
            a = slope*slope + 1
            b = 2*slope*q - 2*xc
            c = q*q + xc*xc - r*r

            return get_abc_roots(a, b, c)
        solutions = get_roots()
        if solutions is None:
            return None
        if len(solutions) > 1:
            xs1, xs2 = solutions
            pa1 = (xs1, f(xs1))
            pa2 = (xs2, f(xs2))
            return xs1 if pa1 == get_closest_point(direction_point, [pa1, pa2]) else xs2
        return solutions[0]
    xs = get_solution()
    if xs is None:
        return None
    point = xs, f(xs)
    distance = get_point_distance(point, circle_center)
    if distance - radius >= 1.0:
        print("Point is found, but not in circle! point: {0}, center: {1}, radius: {2}, distance: {3}"
              .format(point, circle_center, radius, distance))
    return point


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


def get_pixel(image, position):
    x, y = position
    x = int(x)
    y = int(y)

    pformat = 'RGBA'
    format_length = len(pformat)
    image_data = image.get_image_data()
    width = image_data.width
    pitch = image_data.width * format_length
    data = image_data.get_data(pformat, pitch)
    pos = (width*y + x) * format_length
    pixels = data[pos: pos + format_length]

    return tuple(color for color in pixels)


def get_list_of_points_from_list_of_coordinates(list_of_coords, point_count):
    list_of_points = []
    for point_index in range(point_count):
        x = list_of_coords[0 + 2*point_index]
        y = list_of_coords[1 + 2*point_index]
        list_of_points.append((x, y))
    return list_of_points


def get_translated_list_of_coords(list_of_coords, point_count, translation, as_points=False):
    dx, dy = translation
    translated_list = []
    for point_index in range(point_count):
        x = list_of_coords[0 + 2*point_index] + dx
        y = list_of_coords[1 + 2*point_index] + dy
        if as_points:
            translated_list.append((x, y))
        else:
            translated_list.append(x)
            translated_list.append(y)
    return translated_list


def average_list_of_points(list_of_points):
    n = len(list_of_points)
    sum_x = 0
    sum_y = 0
    for x, y in list_of_points:
        sum_x += x
        sum_y += y
    return sum_x/n, sum_y/n


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


def rotate_list_of_points_around_point(list_of_points, axis_point, theta):
    list_of_rotated_points = []
    for point in list_of_points:
        list_of_rotated_points.extend(rotate_point_around_point(point, axis_point, theta))
    return list_of_rotated_points


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


def subtract_points(p, q):
    return p[0]-q[0], p[1]-q[1]


def multiply_points(p, q):
    return p[0]*q[0], p[1]*q[1]


def divide_points(p, q):
    return p[0]/q[0], p[1]/q[1]

colors = Colors()


import pyglet
from pyglet.window import key


# pyglet-specific library
class PygletLib:
    # Abstract observer class
    class Observer(object):
        def __init__(self, subject):
            subject.push_handlers(self)

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

