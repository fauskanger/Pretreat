import math
import pyglet
from app.pythomas import pythomas as lib
from app.config import config


class Shape(object):
    def __init__(self, position, color=None, color_list=None, mode=pyglet.gl.GL_POLYGON, anchor=None,
                 batch=None, group=None, z=0):
        self.x = position[0]
        self.y = position[1]
        self.z = z
        # self.draw_points_list = None  # self.create_draw_points()
        self.vertex_list = None  # self.create_vertex_list()
        if False:
            self.vertex_list = pyglet.graphics.vertex_list(0, None)
        self.translate = None
        self.color_list = [] if not color_list else color_list
        self.color = color
        if color:
            self.color_list = None
        self.mode = mode
        self.rotation_anchor = self.get_position() if not anchor else anchor
        self.batch = batch
        self.batch_group = pyglet.graphics.OrderedGroup(self.z)
        self.added_to_batch = False
        self.is_initialized = False

    def set_batch(self, batch, group=pyglet.graphics.Group()):
        dirty = False
        if batch and batch is not self.batch:
            self.batch = batch
            dirty = True
        if group and group is not self.batch_group:
            self.batch_group = group
            dirty = True
        self.update_shape(dirty)

    def set_z(self, z):
        self.z = z
        self.batch_group = pyglet.graphics.OrderedGroup(z)
        self.update_shape(dirty=True)

    # Does NOT work: batch.add(count, mode, group, *data)
    # def get_batch_parameters(self):
    #     data = (config.world.vertex_mode, self.vertex_list.vertices), \
    #            (config.world.color_mode, self.vertex_list.colors)
    #     return self.vertex_list.count, self.mode, self.batch_group, data

    def delete(self):
        if self.vertex_list:
            self.vertex_list.delete()
            self.vertex_list = None

    def set_position(self, new_position):
        x, y = new_position
        dx, dy = x - self.x, y - self.y
        self.x = x
        self.y = y
        self.set_anchor(lib.sum_points((dx, dy), self.rotation_anchor))
        if self.vertex_list:
            for i in range(self.vertex_list.count):
                xi, yi = 2*i, 2*i+1
                self.vertex_list.vertices[xi] += dx
                self.vertex_list.vertices[yi] += dy

    def move(self, dx, dy):
        self.set_position(lib.sum_points(self.get_position(), (dx, dy)))

    def set_anchor(self, anchor_point):
        self.rotation_anchor = anchor_point

    def rotate(self, theta, anchor_point=None):
        anchor_point = anchor_point if anchor_point else self.rotation_anchor
        rotated_points = []
        for point_index in range(self.vertex_list.count):
            x = self.vertex_list.vertices[0 + 2*point_index]
            y = self.vertex_list.vertices[1 + 2*point_index]
            point = x, y
            rotated_points.extend(lib.rotate_point_around_point(point, anchor_point, theta))
        self.vertex_list.vertices = rotated_points
        return self.vertex_list.vertices

    def create_draw_points(self):
        return None

    def get_position(self):
        return self.x, self.y

    def set_color(self, color):
        self.color = color
        if self.vertex_list:
            self.update_color_list(self.vertex_list.count)
            self.vertex_list.colors = self.color_list

    def update_color_list(self, number_of_vertices):
        # if number_of_vertices is None and self.vertex_list:
        #     number_of_vertices = self.vertex_list.count
        # else:
        #     return None
        count_needed = 3*number_of_vertices

        def get_diff():
            return len(self.color_list) - count_needed
        if self.color:
            self.color_list = list(self.color*number_of_vertices)
        elif self.color_list is None:
            print("Warning: Updated color to red from default color.")
            self.color_list = list(lib.colors.red*number_of_vertices)
        elif get_diff() != 0:
            while get_diff() > 0:
                self.color_list.remove(self.color_list[-1])
            while get_diff() < 0:
                self.color_list.append(self.color_list[0])
        return self.color_list

    def create_vertex_list(self):
        # Create a vertex list from shape attributes
        points = self.create_draw_points()
        if False:
            points = []
        if points is None:
            return None
        number_of_vertices = int(len(points)/2)
        self.update_color_list(number_of_vertices)

        if self.vertex_list:
            self.vertex_list.delete()
            self.vertex_list = None
        if self.batch:
            data = (config.world.vertex_mode, tuple(points)), \
                   (config.world.color_mode, tuple(self.color_list))
            group = pyglet.graphics.Group(pyglet.graphics.OrderedGroup(self.z))
            # self.vertex_list = self.batch.add(number_of_vertices, self.mode, self.batch_group, *data)
            self.vertex_list = self.batch.add(number_of_vertices, self.mode, group, *data)
        else:
            self.vertex_list = pyglet.graphics.vertex_list(number_of_vertices,
                                                           config.world.vertex_mode,
                                                           config.world.color_mode)
        return self.vertex_list

    def update_shape(self, dirty=False):
        # if not self.translate and not self.draw_points_list:
        # self.update_draw_points()
        if not self.is_initialized or dirty:
            self.create_vertex_list()
            self.is_initialized = True

    def draw(self, batch=None):
        # TODO: Fix batched draw
        if self.vertex_list is None:
            return
        if batch and not self.batch:
            self.set_batch(batch)
        elif self.batch is None:
            # pyglet.graphics.draw(self.vertex_list.get_size(), mode, self.vertex_list)
            print("WARNING: Not drawing in batch!")
            self.vertex_list.draw(self.mode)

    def get_centroid(self):
        return lib.average_list_of_points(
            lib.get_list_of_points_from_list_of_coordinates(self.vertex_list.vertices, self.vertex_list.count)
        )


class Circle(Shape):
    def __init__(self, position, radius, color, batch=None, z=0):
        Shape.__init__(self, position, color, mode=pyglet.gl.GL_TRIANGLE_FAN, batch=batch, z=z)
        self.radius = radius
        self.update_shape()

    def create_draw_points(self):
        return lib.get_circle_points(center=(self.x, self.y),
                                     radius=self.radius,
                                     include_center=True)

    def set_radius(self, radius):
        if radius >= 0.0 and radius != self.radius:
            self.radius = radius
            self.update_shape(dirty=True)

    def expand_radius(self, value):
        if -value < self.radius and value != 0.0:
            self.set_radius(self.radius+value)


class Rectangle(Shape):
    def __init__(self, start_point, end_point, radius, colors_list=None, color=None, batch=None, z=0):
        Shape.__init__(self, position=lib.get_middle(start_point, end_point),
                       color=color, color_list=colors_list, mode=pyglet.gl.GL_QUADS, batch=batch, z=z)
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
        self.update_shape()

    @staticmethod
    def create_centerd_on(position, width, height=None, theta=0, colors_list=None, color=None, batch=None):
        height = width if not height else height
        start = lib.sum_points(position, (-width/2, 0))
        end = lib.sum_points(position, (width/2, 0))
        rect = Rectangle(start, end, height, colors_list, color, batch)
        if theta != 0:
            rect.rotate(theta)
        return rect

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


class Triangle(Shape):
    def __init__(self, base_center, base_width, height=None, rotation=0.0,
                 colors_list=None, color=None, anchor=None, batch=None, z=0):
        Shape.__init__(self, position=base_center, color=color, color_list=colors_list,
                       mode=pyglet.gl.GL_TRIANGLES, anchor=anchor, batch=batch, z=z)
        if height is None:
            height = base_width * 0.866  # math.sqrt(3)/2
        self.width = base_width
        self.height = height
        self.rotation = rotation
        self.update_shape()

    @staticmethod
    def create_with_centroid(centroid, base_width, height=None, rotation=0.0,
                             colors_list=None, color=None, z=0):
        if height is None:
            height = base_width * 0.866  # math.sqrt(3)/2
        base_left = centroid[0] - base_width/2, centroid[1]
        base_right = centroid[0] + base_width/2, centroid[1]
        tip = centroid[0], centroid[1] + height
        desired_centroid = centroid
        current_centroid = lib.average_list_of_points([base_right, base_left, tip])
        offset = lib.subtract_points(current_centroid, desired_centroid)
        position = lib.subtract_points(centroid, offset)
        triangle = Triangle(position, base_width, height, rotation,
                            colors_list, color, anchor=centroid, z=z)
        triangle.set_anchor(centroid)
        return triangle

    def create_draw_points(self):
        default_rotation = math.pi / 2
        base_left = self.x - self.width/2, self.y
        base_right = self.x + self.width/2, self.y
        tip = self.x, self.y + self.height
        triangle_points = [base_left, base_right, tip]
        rotated_triangle_points = []
        anchor = self.rotation_anchor
        for p in triangle_points:
            rotated_p = lib.rotate_point_around_point(p, anchor, self.rotation - default_rotation)
            rotated_triangle_points.extend(rotated_p)
        return rotated_triangle_points

    def set_height(self, height):
        self.height = height
        self.update_shape(dirty=True)

    def set_width(self, width):
        self.width = width
        self.update_shape(dirty=True)


class OutlinedCircle(Circle):
    def __init__(self, position, radius, color, border=1.5, outline_color=lib.colors.black, batch=None, z=0, dz=1):
        Circle.__init__(self, position, radius, color, batch=batch, z=z)
        self.border = border
        self.outlined_shape = Circle(position, radius+border, outline_color, z=z-dz)
        self.is_drawing_outline = True
        self.has_rotated = False

    def set_anchor(self, anchor_point):
        super(OutlinedCircle, self).set_anchor(anchor_point)
        self.outlined_shape.set_anchor(anchor_point)

    def set_position(self, new_position):
        super(OutlinedCircle, self).set_position(new_position)
        self.outlined_shape.set_position(new_position)

    def move(self, dx, dy):
        super(OutlinedCircle, self).move(dx, dy)
        self.outlined_shape.move(dx, dy)

    def set_radius(self, radius):
        super(OutlinedCircle, self).set_radius(radius)
        self.outlined_shape.set_radius(radius + self.border)

    def draw(self, batch=None):
        # if not self.has_rotated:
        #     self.outlined_shape.rotate(4*math.pi / self.vertex_list.count)
        #     self.has_rotated = True
        if self.is_drawing_outline:
            self.outlined_shape.draw(batch)
        super(OutlinedCircle, self).draw(batch)

    def toggle_outline(self):
        self.set_outline_draw(not self.is_drawing_outline)

    def set_outline_draw(self, draw_outline):
        if draw_outline == self.is_drawing_outline:
            return
        self.is_drawing_outline = draw_outline
        if self.is_drawing_outline:
            super(OutlinedCircle, self).set_radius(self.outlined_shape.radius - self.border)
        else:
            super(OutlinedCircle, self).set_radius(self.outlined_shape.radius)

    def delete(self):
        super(OutlinedCircle, self).delete()
        self.outlined_shape.delete()




























