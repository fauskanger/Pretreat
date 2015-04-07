import math

from app.config import config
from app.pythomas import pythomas as lib
from app.pythomas import shapes as shapelib


class Edge:
    def __init__(self, from_node, to_node):
        self.z = config.world.z_indexes.path
        self.from_node = from_node
        self.to_node = to_node
        self.inner_from_shape = None
        self.inner_to_shape = None
        self.from_circle = None
        self.to_circle = None
        self.line_rectangle = None
        self.line_triangles = []
        self.color = config.world.edge_triangle_color
        self.is_path_edge = False
        self.update_shape()

    def get_from_point(self):
        if self.from_circle:
            return self.from_circle.get_position()
        return None

    def get_to_point(self):
        if self.to_circle:
            return self.to_circle.get_position()
        return None

    def draw(self, batch=None):
        if self.line_rectangle.color != self.color:
            self.line_rectangle.set_color(self.color)
        self.line_rectangle.draw(batch)
        for triangle in self.line_triangles:
            if triangle.color != self.color:
                triangle.set_color(self.color)
            triangle.draw(batch)
        # self.inner_from_shape.draw(batch)
        # self.inner_to_shape.draw(batch)
        self.from_circle.draw(batch)
        self.to_circle.draw(batch)

    def update_shape(self):
        from_node = self.from_node
        to_node = self.to_node

        from_x, from_y = from_node.get_position()
        to_x, to_y = to_node.get_position()
        theta = math.atan2(to_y-from_y, to_x-from_x)

        def get_pos_offset(node):
            offset_radius = config.world.edge_lane_offset
            if node.is_selected() and config.world.adjust_edge_to_selection:
                offset_radius += config.world.selected_radius_decrease
            dx = offset_radius * math.sin(theta)
            dy = offset_radius * math.cos(theta)
            offset = dx, -dy
            return offset

        from_offset = get_pos_offset(from_node)
        to_offset = get_pos_offset(to_node)
        from_position = lib.sum_points(from_node.get_position(), from_offset)
        to_position = lib.sum_points(to_node.get_position(), to_offset)

        from_circle_point = lib.get_point_on_circle(circle_center=from_node.get_position(),
                                                    radius=from_node.get_visual_radius(),
                                                    line_point=from_position,
                                                    direction_point=to_position)

        to_circle_point = lib.get_point_on_circle(circle_center=to_node.get_position(),
                                                  radius=to_node.get_visual_radius(),
                                                  line_point=to_position,
                                                  direction_point=from_position)

        point_difference = lib.subtract_points(to_circle_point, from_circle_point)
        line_distance = lib.get_point_distance(from_circle_point, to_circle_point)
        self.update_circles(from_circle_point, to_circle_point)

        colors = list(config.world.edge_color * 4)
        if from_circle_point is None or to_circle_point is None:
            print("Could not draw to circle.")
            # self.shape = shapelib.Rectangle(from_position, to_position,
            #                                 config.world.edge_thickness, colors_list=colors)
            # self.inner_from_shape = self.inner_to_shape = None
        else:
            if self.line_rectangle:
                self.line_rectangle.delete()
            self.line_rectangle = shapelib.Rectangle(from_circle_point, to_circle_point,
                                                     config.world.edge_thickness, colors_list=colors, z=self.z-1)

            def add_triangles():
                def delete_old_triangles():
                    for old_triangle in self.line_triangles:
                        old_triangle.delete()
                    self.line_triangles.clear()
                delete_old_triangles()
                triangle_color = self.color
                triangle_base_width = config.world.edge_triangles_width
                triangle_height = 0.866 * triangle_base_width  # sqrt(3)/2
                triangle_count = int(line_distance / triangle_height)
                pdx, pdy = point_difference
                steps = pdx/triangle_count, pdy/triangle_count
                for i in range(triangle_count):
                    position = lib.sum_points(from_circle_point, lib.multiply_points(steps, (i, i)))
                    triangle = shapelib.Triangle.create_with_centroid(centroid=position, base_width=triangle_base_width,
                                                                      height=triangle_height, rotation=theta,
                                                                      color=triangle_color, z=self.z)
                    self.line_triangles.append(triangle)
            add_triangles()
            inner_color = config.world.edge_in_node_color
            inner_line_width = 4
            if self.inner_from_shape:
                self.inner_from_shape.delete()
            if self.inner_to_shape:
                self.inner_to_shape.delete()
            self.inner_from_shape = shapelib.Rectangle(from_node.get_position(), self.from_circle.get_position(),
                                                       radius=inner_line_width, color=inner_color, z=from_node.z+1)
            self.inner_to_shape = shapelib.Rectangle(to_node.get_position(), self.to_circle.get_position(),
                                                     radius=inner_line_width,  color=inner_color, z=to_node.z+1)

    def set_color(self, color):
        self.color = color

    def set_as_path_edge(self, is_path_edge=True):
        self.is_path_edge = is_path_edge
        if is_path_edge:
            self.set_color(config.world.path_edge_color)
        else:
            self.set_color(config.world.edge_triangle_color)

    def update_circles(self, from_circle_point, to_circle_point):
        if from_circle_point is not None:
            if self.from_circle:
                self.from_circle.set_position(from_circle_point)
            else:
                self.from_circle = shapelib.Circle(from_circle_point, config.world.edge_end_radius, lib.colors.black)
        if to_circle_point is not None:
            if self.to_circle:
                self.to_circle.set_position(to_circle_point)
            else:
                self.to_circle = shapelib.Circle(to_circle_point, config.world.edge_end_radius, lib.colors.black)

    def delete(self):
        if self.line_rectangle:
            self.line_rectangle.delete()
        for triangle in self.line_triangles:
            triangle.delete()
        if self.inner_from_shape:
            self.inner_from_shape.delete()
        if self.inner_to_shape:
            self.inner_to_shape.delete()
        if self.from_circle:
            self.from_circle.delete()
        if self.to_circle:
            self.to_circle.delete()

