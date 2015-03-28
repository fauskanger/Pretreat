import pyglet
from enum import Enum

from app.config import config
from app.pythomas import shapes as shapelib


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
        self.x = int(x)
        self.y = int(y)
        self.label = "{0},{1}".format(x, y)
        self.altitude = altitude
        self.content = content
        self.batch_group = pyglet.graphics.OrderedGroup(config.world.node_order_index)
        self.printed = False
        self.circle = shapelib.Circle((x, y), self.current_radius, self.current_color)
        self.select_circle = None
        self.state = self.State.Default
        self._is_selected = is_selected

    def set_as_selected(self, selected):
        self._is_selected = selected
        self.update_selected_indicator()

    def is_selected(self):
        return self._is_selected

    def update_selected_indicator(self):
        selected_radius = self.get_radius() + config.world.selected_radius_increase
        color = config.world.selected_node_color
        if self.select_circle is None:
            self.select_circle = shapelib.Circle(position=self.get_position(), radius=selected_radius, color=color)
        self.select_circle.set_radius(selected_radius)
        self.select_circle.set_color(color)

    def set_radius(self, new_radius):
        self.current_radius = new_radius
        self.circle.set_radius(self.current_radius)
        self.update_selected_indicator()

    def set_state(self, state):
        print("Setting new state: {0}".format(state))
        self.set_color(Node.get_state_color(state))
        self.state = state

    def set_position(self, new_position):
        if new_position is None:
            return False
        self.x = new_position[0]
        self.y = new_position[1]
        self.circle.set_position(new_position)
        if self.select_circle is not None:
            self.select_circle.set_position(new_position)
        self.update_parameters()
        return True

    def update_parameters(self):
        self.label = "{0},{1}".format(self.x, self.y)
        pass

    def get_radius(self):
        return self.current_radius

    def get_padded_radius(self):
        padding = config.world.selected_radius_increase+config.world.node_padding
        return self.get_radius() + padding

    def get_visual_radius(self):
        extra = 0.0
        if self.is_selected():
            extra += config.world.selected_radius_increase
        return self.get_radius()+extra

    def get_position(self):
        return self.x, self.y

    def draw_selected_indicator(self, batch=None):
        if self.is_selected():
            if self.select_circle is None:
                self.update_selected_indicator()
            self.select_circle.draw(batch)

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

    def delete(self):
        if self.circle:
            self.circle.delete()
        if self.select_circle:
            self.select_circle.delete()

    def update(self, dt):
        pass

