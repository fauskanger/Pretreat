import pyglet
from enum import Enum

from app.config import config
from app.pythomas import pythomas as lib, shapes as shapelib


class Node:
    class State(Enum):
        Default = 0
        Start = 1
        Destination = 2

    @staticmethod
    def get_state_color(state):
        states_colors = {
            Node.State.Default: config.world.node_color,
            Node.State.Start: config.world.start_node_color,
            Node.State.Destination: config.world.destination_node_color,
            }
        return states_colors[state]

    def __init__(self, x, y, altitude=0, content=None, is_selected=False):
        self.current_radius = config.world.node_radius
        self.default_color = config.world.node_color
        self.current_color = self.default_color
        self.x = x
        self.y = y
        self.z = config.world.z_indexes.node
        self.z_path = self.z - 10
        self.z_selected = self.z_path - 10
        self.label = None
        text_label = "" if not self.label else self.label
        self.text_label = pyglet.text.Label(text_label,
                                            font_name='Times New Roman',
                                            font_size=0.61*self.current_radius,
                                            x=self.x, y=self.y,
                                            anchor_x='center', anchor_y='center',
                                            color=lib.rgba(config.world.node_label_color),
                                            group=pyglet.graphics.OrderedGroup(-100000))
        self.altitude = altitude
        self.content = content
        self.occupants = []
        self.batch_group = pyglet.graphics.OrderedGroup(config.world.node_order_index)
        self.circle = shapelib.OutlinedCircle((x, y), self.current_radius, self.current_color, z=self.z, dz=1)
        self.path_circle = None
        self.select_circle = None
        self.state = self.State.Default
        self._is_path_node = False
        self._is_selected = is_selected

    def add_occupant(self, occupant):
        if occupant not in self.occupants:
            self.occupants.append(occupant)
            return True
        return False

    def remove_all_occupants(self):
        self.occupants.clear()

    def remove_occupant(self, occupant):
        return lib.try_remove(self.occupants, occupant)

    def has_occupants(self):
        return len(self.occupants) > 0

    def get_distance_to(self, node):
        return lib.get_point_distance(self.get_position(), node.get_position())

    def set_label(self, label):
        self.label = label
        self.text_label.text = self.label

    def set_as_selected(self, selected):
        self._is_selected = selected
        if selected:
            pos = self.get_position()
            radius = self.get_selected_radius()
            color = config.world.selected_node_color
            if self.select_circle is None or self.select_circle.radius != radius:
                self.select_circle = shapelib.OutlinedCircle(pos, radius=radius, color=color, z=self.z_selected)
        elif self.select_circle:
            self.select_circle.delete()
            self.select_circle = None

    def set_as_path_node(self, is_path_node=True):
        self._is_path_node = is_path_node
        if is_path_node:
            pos = self.get_position()
            radius = self.get_path_radius()
            color = config.world.path_edge_color
            if not self.path_circle:
                self.path_circle = shapelib.OutlinedCircle(pos, radius, color, z=self.z_path)
        else:
            if self.path_circle:
                self.path_circle.delete()
                self.path_circle = None

    def is_selected(self):
        return self._is_selected

    def is_path_node(self):
        return self._is_path_node

    def update_selected_indicator(self):
        if self.is_selected():
            circle = self.select_circle
            pos = self.get_position()
            radius = self.get_selected_radius()
            color = config.world.selected_node_color
            if circle.get_position() != pos:
                circle.set_position(pos)
            if circle.radius != radius:
                circle.set_radius(radius)
            if circle.color != color:
                circle.set_color(color)

    def update_path_indicator(self):
        if self.is_path_node():
            circle = self.path_circle
            pos = self.get_position()
            radius = self.get_path_radius()
            color = config.world.path_edge_color
            if circle.get_position() != pos:
                circle.set_position(pos)
            if circle.radius != radius:
                circle.set_radius(radius)
            if circle.color != color:
                circle.set_color(color)

    def set_radius(self, new_radius):
        self.current_radius = new_radius
        self.circle.set_radius(self.current_radius)

    def set_state(self, state):
        # print("Setting new state: {0}".format(state))
        self.state = state

    def move(self, dx, dy):
        self.set_position((self.x + dx, self.y + dy))

    def set_position(self, new_position):
        if new_position is None:
            return False
        self.x, self.y = new_position
        self.circle.set_position(new_position)
        self.text_label.x, self.text_label.y = new_position
        if self.select_circle:
            self.select_circle.set_position(new_position)
        if self.path_circle:
            self.path_circle.set_position(new_position)
        return True

    def get_radius(self):
        return self.current_radius

    def get_padded_radius(self):
        padding = config.world.node_padding
        return self.get_visual_radius() + padding

    def get_path_radius(self):
        return self.get_radius()+config.world.path_radius_increase

    def get_selected_radius(self):
        if self.is_path_node():
            return self.get_path_radius()+config.world.selected_radius_increase
        else:
            return self.get_radius()+config.world.selected_radius_increase

    def get_visual_radius(self):
        if self.is_selected():
            return self.get_selected_radius()
        if self.is_path_node():
            return self.get_path_radius()
        return self.get_radius()

    def get_position(self):
        return self.x, self.y

    def draw_label(self):
        if self.text_label:
            self.text_label.draw()

    def draw_selected_indicator(self, batch=None):
        if self.is_selected() and self.select_circle:
            self.select_circle.draw(batch)

    def draw_path(self, batch=None):
        if self.is_path_node() and self.path_circle:
            self.path_circle.draw(batch)

    def draw(self, radius_offset=0.0, batch=None):
        def draw_circle():
            if radius_offset == 0.0:
                self.circle.draw(batch)
            else:
                self.circle.expand_radius(-radius_offset)
                self.circle.draw(batch)
                self.circle.expand_radius(radius_offset)

        draw_circle()

    def set_color(self, color):
        self.circle.set_color(color)

    def get_color(self):
        return self.circle.color if self.circle.color else config.world.node_color

    def delete(self):
        if self.circle:
            self.circle.delete()
        if self.select_circle:
            self.select_circle.delete()
        if self.path_circle:
            self.path_circle.delete()

    def update(self, dt):
        self.set_color(Node.get_state_color(self.state))
        self.update_path_indicator()
        self.update_selected_indicator()
        if self.has_occupants():
            self.set_color(config.world.node_occupied_color)

