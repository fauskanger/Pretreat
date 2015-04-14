# Pretreat
Clone this repository:
```sh
$ git clone https://github.com/fauskanger/Pretreat.git
```
## Summary
A graph editor for examining pathfinding algorithms that take tactical retreat / withdrawal options into consideration. 
I.e. an agent might be instructed to retreat or back up from a node during a walk along an a priori optimal path. 
This application is meant to provide the basic tools to illustrate and test such algorithms.

  
  

## How to use
  1. Start application with run.py
  2. Create a directed graph by adding nodes and edges.
  3. Set start and destination nodes.
  4. Pathfinder starts when both ends are defined.
  

LMB, RMB and MMB is short for Left/Right/Middle Mouse Button:

### Nodes
| Event         | Input         | Alternative |
| :------------- |:-------------|:----|
| Add Node      | Ctrl + RMB | RMB|
| Remove Node      | Alt + RMB      |
| Select a Node | LMB |
| Add Node to selection | Ctrl + LMB|
| Remove Node from selection | Alt + LMB|
| Move Selected Nodes | MMB + Drag      |
| Toggle Block on Selected Nodes | B      |

### Edges
When one or more nodes are selected:

| Event         | Input         |
| :------------- |:-------------|
| Add From Selected To       | Ctrl + RMB |
| Add To Selected From      | Ctrl + Shift + RMB |
| Remove From Selected To        | Alt + RMB |
| Remove To Selected From       | Alt + Shift + RMB |
| Add/Remove both To and From      | RMB |

### Pathfinding
| Event         | Input         | Alternative |
| :------------- |:-------------|:----|
| Set Start\* | S + LMB| S, then LMB |
| Set Destination\* | D + LMB| D, then LMB |
| Complete Search\*\*      | Space |

\*) S and D keypress might block trackpad's mouse-press. Not an issue when using a separate mouse.
\*\*) Applicable when pathfinding algorithm is illustrated step by step.

### Miscellaneous
| Event         | Input         |
| :------------- |:-------------|
| Generate Grid of Nodes      | G |
| Toggle Background (Altitude Map)      | A |

  
  

## Technical
### Requirements
  - Math-library: NumPy [ [Official](http://www.numpy.org/) | [Wheels](http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy) ]
  - Installation package: Setuptools [ [Offical](https://pypi.python.org/pypi/setuptools) ] - required by NetworkX
  - Graph library: NetworkX 1.9.1 [ [How to install](http://networkx.github.io/documentation/networkx-1.9.1/install.html) ]
  - Windowing and multimedia library: Pyglet 1.2 [ [How to install](http://www.pyglet.org/download.html) ]

### Current/working Setup
  - Developed with 64-bit version of Python 3.4.2 (Kit: [Anaconda Python Package](https://store.continuum.io/cshop/anaconda/))
  - Anaconda includes the following used/required packages: (See "Requirements")
    - NumPy
    - Setuptools
  - Tested on Windows 7 and 8
  - IDE used: JetBrain's PyCharm (Free Academic Licence) [ [Download here](https://www.jetbrains.com/pycharm/download/) ]

(It seems that http://www.lfd.uci.edu/~gohlke/pythonlibs/ is a great source of Python libraries across platforms and versions.) 

### Comments on the code
```python
class Foo:
    def __init__(self, bar=None):
        self.bar = bar
        if False:
            self.bar = SomeKnownType()
```
The above is used to improve autocompletion in PyCharm, 
so that it will suggest attributes from `self.bar` relevant to the known type.
This is not only used in `__init__`, but the hidden type of `bar` is an example of motivation, 
and IDE-functionality like "Go to declaration" is another.

### Some central components
  - [NavigationGraph](app/classes/graph/navigation_graph.py) - Interactive graph w/pathfinder.
  - [Pathfinder](app/classes/graph/pathfinder.py) - Base for pathfinders, implementations of search algorithms.
  - [PretreatPathfinder](app/classes/graph/pretreat_pathfinder.py) - Custom pathfinder considering retreat.
  - [Path](app/classes/graph/path.py) - The intermediate or final result of a pathfinder, holding the path nodes.
  - [MainWindow](app/classes/windows/main_window.py) - Main window class.
  - [Configurations](app/config.py) - Configurations, constants and setup for the applications.

The NetworkX graph allows for the use of 
[any](https://networkx.github.io/documentation/latest/tutorial/tutorial.html#what-to-use-as-nodes-and-edges) 
node and edge representation. The graph contains all relations between them, so the representations don't have to. 
Read more about NetworkX node/edge attributes in their 
[tutorial](https://networkx.github.io/documentation/latest/tutorial/tutorial.html#adding-attributes-to-graphs-nodes-and-edges).

This project use the [Node](app/classes/graph/node.py) and 
[Edge](app/classes/graph/edge.py) class to handle rendering and graph-agnostic logic, 
but can still put values essential to the pathfinder such as edge weights in the graph itself for efficiency.
 
Pyglet offers no primitives, so the [pythomas shapes](app/pythomas/shapes.py) are used for all non-sprites. Also, 
several modules depend on one or more of the functions in the [pythomas library](app/pythomas/pythomas.py).

  
  

#### NavigationGraph
View the whole file: [app/classes/graph/navigation_graph.py]()
```python
import networkx as nx


class NavigationGraph():
    def __init__(self):
        self.graph = nx.DiGraph()
        self.pathfinder = AStarPathfinder(self.graph, self.altitude_function)
        self.pathfinder.push_handlers(self)
        # ...
```

The NavigationGraph class is a wrapper around 
NetworkX' [DiGraph](http://networkx.github.io/documentation/networkx-1.9.1/tutorial/tutorial.html#directed-graphs) 
class, and offers a convenient interface to common graph interactions. It calls `draw()` on all graph 
objects, and also ties together a pathfinder to its graph.

```
    def on_path_update(self, path):
        # ...
```

An `on_path_update`-event is dispatched when the pathfinder
has updated its path.

```
    def create_node(self, position)
    
    def add_node(self, node)
    def remove_node(self, node)
    def set_node_position(self, node, new_position)
    def move_node(self, node, dx, dy)
```

Basic node operations. The `create_node` factory inserts the correct altitude into the node object at the position.

```
    def _set_node_state(self, node, state)
    def set_node_state(self, node, state)
    
    def set_node_to_default(self, node)    
    def set_start_node(self, node)
    def set_destination_node(self, node)
    
    def start_pathfinding(self)
    def refresh_path_radius(self)
```

Manage pathfinding. `_set_node_state` is used internally in the latter methods.

```
    def select_node(self, node)
    def select_node_at_position(self, position)
    
    def deselect_node(self, node)
    def deselect_node_at_position(self, position)
    def deselect_all_nodes(self)
    
    def toggle_select(self, node, compare=None)
    def get_selected_nodes(self)
```

Control selection of nodes.

```
    def add_edge(self, from_node, to_node)    
    def remove_edge(self, from_node, to_node)
    def get_edge_object(self, edge)
    
    def create_edge_from_selected_to(self, node)
    def create_edge_to_selected_from(self, node)
    
    def remove_edges_from_many(self, to_node, from_nodes)
    def remove_edges_to_many(self, from_node, to_nodes)
    
    def remove_all_node_edges(self, node)
    
    def update_node_edges(self, node)
    def redraw_edges(self, node)
    def redraw_all_edges(self)
```
Edge management. Each edge is only refreshed on a configured interval, and the edges to be refreshed are managed
through the last methods above. 

`get_edge_object` is useful to retrieve the [Edge](app/classes/graph/edge.py)-instance, and accepts both a 
(node_u, node\_v)-tuple or an edge returned from the `self.graph.edges()`-iterator. 

```
    def block_node(self, node)
    def unblock_node(self, node)
```
Add an occupant to the node, i.e. obstruct search algorithm in pathfinder from visiting the node. Currently this is
ensured by setting any edge ending in an obstructed node to have an infinite cost in the form `float("inf")`.

```
    def get_altitude(self, position)
    def altitude_function(self, from_node, to_node)
```

A height-map imported from file determines the terrain's altitude at a given position. This is used by pathfinder to
consider path slopes. 

```
    def get_node_from_position(self, position)
    def is_valid_node_position(self, position, node_exceptions=None)
    def find_nearest_nodes(self, node, number_of_hits=1, candidates=None, exceptions=())
    def generate_grid_with_margin(self, rows, cols, margin, width, height)
    def generate_grid(self, row_count, col_count, max_width, max_height, start_pos=(0, 0), make_hex=True)
```

Some helper methods.    

```
    def draw(self)
    def update(self, dt)
    def update_nodes(self, dt)
    def update_edges(self, dt)
    def update_path(self, dt)
    def update_node_labels(self)
    def clear(self)
```
Render and update.

  
  

#### Pathfinder
View the whole file: [app/classes/graph/pathfinder.py]().

The Pathfinder class is a base class for all pathfinders, and the later described CustomPathfinder class is a base
class for iterable pathfinders, or for now, the PretreatPathfinder.

```python
class Pathfinder(pyglet.event.EventDispatcher):
    @staticmethod
    def get_event_type_on_path_update():
        return strings.events.on_path_update

    def __init__(self, graph, altitude_function=None):
        self.graph = graph
        self.start_node = None
        self.destination_node = None
        self.path = None
        self.register_event_type(Pathfinder.get_event_type_on_path_update())
        self.altitude_function = altitude_function
```
The [path](app/classes/graph/path.py) is created by the pathfinder in the `update_to_new_path`-method.
Pyglet's event module separate the events using strings, and a user without the config module can use 
a static method `get_event_type_on_path_update` to obtain the corresponding string.
```python
    def get_edge_cost(self, from_node, to_node):
        return lib.get_point_distance(from_node.get_position(), to_node.get_position())
```
The edge cost, e.g. simply the distance. Derived classes overrides to implement their own cost functions.
```

    def set_start_node(self, node)
    def set_destination_node(self, node)
    def clear_node(self, node)
```
Assign and remove end nodes.
```
    def start(self)
    
    def get_path(self)
    def get_path_edges(self)
    def get_path_nodes(self)
```
Start pathfinder and retrieve information.
```
    def update_to_new_path(self, new_path=None)
    def create_path(self)
```
Calling `update_to_new_path` will refresh pathfinder. Within, the `create_path` is called
 to construct the path, i.e. this is where the derived classes present their pathfinding implementation. Also,
 it's using `assemble_waypoint_paths` to include waypoints, which is described below.
```
    def notify_node_change(self, node)
    def split_path_on_waypoint(self, node)
    
    def add_waypoint(self, node, index=None)
    def remove_waypoint(self, node)
    def waypoint_index(self, node)
    def assemble_waypoint_paths(self)
```
The NavigationGraph will `notify_node_change` when the node's occupant-list is changed. When a node is blocked,
the pathfinder will call `split_path_on_waypoint` with blocked node's predecessor.

Adding waypoints in essence creates multiple, consecutive paths between them, that are retrieved as a
flattened list of nodes from `assemble_waypoints`. Tbe `create_path`-method mentioned above is used to find the path 
between each waypoint.
```
    def update(self, dt)
    def _update(self, dt)
    def draw(self, batch=None)
```
Update and render. The `_update` method is used to control iteration time intervals in e.g. CustomPathfinder.

  
  
##### AStarPathfinder

```python
class AStarPathfinder(Pathfinder):
    def __init__(self, graph, altitude_function=None):
        Pathfinder.__init__(self, graph, altitude_function)

        def heuristics(from_node, to_node):
            return from_node.get_distance_to(to_node)
        self.heuristic_function = heuristics

    def create_path(self):
        if self.start_node and self.destination_node:
            try:
                nodes = nx.astar_path(self.graph, self.start_node, self.destination_node, self.heuristic_function)
            except nx.NetworkXNoPath:
            nodes = []  # No path found.
        return Path(nodes)
```
A simple implementation of
[NetworkX' A\* Algorithm](https://networkx.github.io/documentation/latest/reference/generated/networkx.algorithms.shortest_paths.astar.astar_path.html).
The `create_path` simply return a [Path](app/classes/graph/path.py) object based on the list of nodes.


  
  
##### CustomPathfinder

```python
class CustomPathfinder(Pathfinder):
    class State(Enum):
        Unassigned = 0
        Running = 1
        Paused = 2
        Stopped = 3

    def __init__(self, graph, name, altitude_function=None):
        Pathfinder.__init__(self, graph, altitude_function)
        self.name = name
        self.is_complete = False
        self.use_steps = False
        self.speed = 1  # Steps per second
        self.ticks_counter = 0
        self.running = False

    def _update(self, dt):
        if self.running:
            if self.use_steps:
                    self.ticks_counter += dt * self.speed
                    ticks = int(self.ticks_counter)
                    if ticks > 0:
                        for t in range(ticks):
                            self.tick()
                        self.ticks_counter -= ticks
            else:
                self.complete_search()
```
The CustomPathfinder is the base iterable pathfinder.
```
    def tick(self)
    def create_path(self)
    
    def start(self)
    def step(self, step_count=1)
    def complete_search(self)
    def toggle_pause(self)
    def pause(self)
    def stop(self)
```
The `tick` is called for each step, managed by the overridden `_update`. `create_path` is mentioned above.

  
  

## License
GPL v2.0 - GNU General Public License Version 2

Full license text: [ [Pretty (.md)](LICENSE.md) | [Plain](LICENSE) ]