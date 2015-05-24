import persistent
import math
import pyglet
from BTrees.OOBTree import OOBTree
from pyglet.window import mouse, key
from app.config import config, seeded_random as random
from app.pythomas import pythomas as lib, shapes as shapelib
from app.classes.windows.main_window import BaseWindow

from app.classes.persist import PersistentObject, persistent_storage as persist
dbroot = persist.root
db_key_account = 'account_db'
account_id = 14


class Account(PersistentObject):

    def __init__(self):
        self.balance = 0.0

    def deposit(self, amount):
        self.balance += amount

    def cash(self, amount):
        assert amount <= self.balance
        self.balance -= amount

    def print_balance(self):
        print("Balance: {0}".format(self.balance))


class TestWindow(BaseWindow):
    def __init__(self, outer_handler=None):
        super().__init__("TestWindow", outer_handler)
        self.shapes = []
        self.batch = pyglet.graphics.Batch()
        self.add_test_objects()
        self.extra_shapes = []
        if db_key_account not in dbroot:
            dbroot[db_key_account] = OOBTree()
        self.account_db = dbroot[db_key_account]
        if account_id not in self.account_db:
            self.account_db[account_id] = Account()
        self.account = self.account_db[account_id]
        self.account.print_balance()

        print("Persist root: >> {0}".format(dbroot))

        # self.set_batch()

    def add_test_objects(self):
        width = 100
        radius = width / 2 / 0.866
        centroid = shapelib.Triangle.create_with_centroid
        triangle1 = centroid(centroid=(100, 100), base_width=100, color=lib.colors.red, rotation=math.pi/2)
        triangle2 = centroid(centroid=(100, 200), base_width=100, color=lib.colors.red, rotation=-math.pi)
        circle = shapelib.Circle(position=(100, 100), radius=radius, color=lib.colors.lime)
        rectangle = shapelib.Rectangle(start_point=(200, 100-radius), end_point=(200, 100+radius),
                                       radius=50, color=lib.colors.blue)
        diagonal = shapelib.Rectangle(start_point=(300, 100), end_point=(400, 200),
                                      radius=50, color=lib.colors.yellow)
        self.shapes.extend([circle, triangle1, rectangle, diagonal, triangle2])

    # def set_batch(self):
    #     for shape in self.shapes:
    #         shape.set_batch(self.batch)

    def on_draw(self):
        for shape in self.shapes:
            shape.draw(batch=self.batch)
        self.batch.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.C:
            try:
                self.account.cash(100)
            except AssertionError:
                self.account.cash(self.account.balance)
        if symbol == key.D:
            self.account.deposit(25)
        if symbol == key.S:
            self.account.commit_transaction()
            print("Account saved:")
        self.account.print_balance()

    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            color = random.choice([lib.colors.red, lib.colors.blue, lib.colors.yellow, lib.colors.lime])
            shape = shapelib.Circle((x, y), 20, color=color)
            self.shapes.append(shape)
            # batch_data = shape.get_batch_parameters()
            # count = batch_data[0]
            # mode = batch_data[1]
            # group = batch_data[2]
            # data = batch_data[3]
            # self.batch.add(count, mode, group, *data)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.RIGHT:
            color = random.choice([lib.colors.red, lib.colors.blue, lib.colors.yellow, lib.colors.lime])
            offset = random.random()*800 - 400
            p1 = 500 + offset, 400 - offset/3
            # p2 = 600 + offset, 400 - offset/3
            # p3 = 600 + offset, 500 - offset/3
            # p4 = 500 + offset, 500 - offset/3
            # points = [p1, p2, p3, p4]

            number_of_vertices = 5  # len(points)
            # flatten = lib.flatten_list_of_tuples
            # coords = lib.get_circle_points(p1, number_of_points=number_of_vertices)  # flatten(points)
            # colors = flatten([color * number_of_vertices])
            # data = (config.world.vertex_mode, coords), \
            #        (config.world.color_mode, colors)
            # self.batch.add(number_of_vertices, pyglet.gl.GL_TRIANGLE_FAN, pyglet.graphics.Group(), *data)
            shape = shapelib.Circle(p1, 20, color, z=int(random.random()*100000))
            shape.set_batch(self.batch)
            # self.shapes.append(shape)
            self.extra_shapes.append(shape)
            # batch_data = shape.get_batch_parameters()
            # count = batch_data[0]
            # mode = batch_data[1]
            # group = batch_data[2]
            # # data = batch_data[3]
            # data = (config.world.vertex_mode, shape.vertex_list.vertices), \
            #        (config.world.color_mode, shape.vertex_list.colors)
            # self.batch.add(count, mode, group, *data)


