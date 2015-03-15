#/usr/bin/env python

import pyglet

from pyglet.window import key

from app.libs.json_map import Map



window = pyglet.window.Window(caption="PyThomas",
                              fullscreen=False,
                              resizable=False,
                              visible=False)

# load the map
fd = pyglet.resource.file("test.json", 'rt')
print("{0}".format(fd))
m = Map.load_json(fd)


# set the viewport to the window dimensions
window.set_size(1000, 300)
m.set_viewport(0, 0, m.p_width, m.p_height)
window.set_visible(True)


dims = [(m.p_width, m.p_height),
        (window.get_size()[0], window.get_size()[1]),
        (window.width, window.height)]
for dim in dims:
    print("{0},{1}".format(dim[0], dim[1]))
#
# # perform some queries to the map data!
#
# # list all the objects
# print("listing all the objects:")
# for obj in m.objectgroups["Objects"]:
#     print(obj)
#
# # is there a "Door1" object?
# print("Door1" in m.objectgroups["Objects"])
#
# # is there aan object in coords 10, 10?
# print((0, 10) in m.objectgroups["Objects"])
#
# # get the object named "Door1"
# print("Star1:", m.objectgroups["Objects"]["Star1"])
#
# # get the object in coords (5, 3)
# print("Obj at (5, 3)", m.objectgroups["Objects"][1, 17])
#
# # list all the objects with type "Door":
# print("listing all the Door objects:")
# for obj in m.objectgroups["Objects"].get_by_type("Star"):
#     print(obj)

print("---- ---- ----")
print("Thing: {0}".format(m.p_width))


@window.event
def on_draw():
    window.clear()
    m.set_viewport(0, 0, window.width, window.height)

    m.draw()
    batch = pyglet.graphics.Batch()

    def draw_square(x, y, width, height):
        points = [x, y, x+width, y, x+width, y+height, x, y+height]
        batch.add(4, pyglet.gl.GL_QUADS, ('v2f', points))
        print(points)
    draw_square(50, 100, 200, 50)
    batch.draw()


@window.event
def on_resize(width, height):
    # if width < 300:
    #     width = 300
    # if height < 300:
    #     height = 300
    m.set_viewport(0, 0, width, height)
    # m.set_viewport(0, 0, window.width, window.height)

@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.F:
        window.set_fullscreen(window.fullscreen)
    if symbol == key.T and modifiers & (key.LSHIFT | key.LSHIFT):
        window.set_size(m.p_width, m.p_height)
    if symbol == key.G:
        window.set_size(400, 300)



pyglet.app.run()

