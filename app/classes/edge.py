import math

from app.config import config
from app.pythomas import pythomas as lib
from app.pythomas import shapes as shapelib


class Edge:
    def __init__(self, from_node, to_node):
        self.shape = None
        self.inner_from_shape = None
        self.inner_to_shape = None
        self.p1_circle = None
        self.p2_circle = None
        self.from_node = from_node
        self.to_node = to_node
        self.update_shape()

    def draw(self, batch=None):
        self.shape.draw(batch)
        self.inner_from_shape.draw(batch)
        self.inner_to_shape.draw(batch)
        self.p1_circle.draw(batch)
        self.p2_circle.draw(batch)

    def update_shape(self):
        from_node = self.from_node
        to_node = self.to_node

        from_x, from_y = from_node.get_position()
        to_x, to_y = to_node.get_position()
        theta = math.atan2(to_y-from_y, to_x-from_x)

        def get_pos_offset(node):
            offset_radius = config.world.edge_lane_offset
            if node.is_selected and config.world.adjust_edge_to_selection:
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

        self.update_circles(from_circle_point, to_circle_point)

        colors = list(config.world.edge_color * 4)
        if from_circle_point is None or to_circle_point is None:
            print("Could not draw to circle.")
            # self.shape = shapelib.Rectangle(from_position, to_position,
            #                                 config.world.edge_thickness, colors_list=colors)
            # self.inner_from_shape = self.inner_to_shape = None
        else:
            self.shape = shapelib.Rectangle(from_circle_point, to_circle_point,
                                            config.world.edge_thickness, colors_list=colors)
            inner_color = lib.colors.extra.green
            inner_line_width = 4
            self.inner_from_shape = shapelib.Rectangle(from_node.get_position(), self.p1_circle.get_position(),
                                                       radius=inner_line_width, color=inner_color)
            self.inner_to_shape = shapelib.Rectangle(to_node.get_position(), self.p2_circle.get_position(),
                                                     radius=inner_line_width,  color=inner_color)

    def update_circles(self, from_circle_point, to_circle_point):
        if from_circle_point is not None:
            if self.p1_circle:
                self.p1_circle.set_position(from_circle_point)
            else:
                self.p1_circle = shapelib.Circle(from_circle_point, config.world.edge_end_radius, lib.colors.red)
        if to_circle_point is not None:
            if self.p2_circle:
                self.p2_circle.set_position(to_circle_point)
            else:
                self.p2_circle = shapelib.Circle(to_circle_point, config.world.edge_end_radius, lib.colors.blue)

