# Pretreat
Clone this repository:
```sh
$ git clone https://github.com/fauskanger/Pretreat.git
```
## Summary
A graph editor for examining pathfinding algorithms that take tactical retreat / withdrawal options into consideration. 
I.e. an agent might be instructed to retreat or back up from a node during a walk along an a priori optimal path. 
This application is meant to provide the basic tools to illustrate and test such algorithms.

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

### Central Components

#### NavigationGraph
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
    def on_path_update(self, path)
    
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
    
    def toggle_select(self, node, compare=None)
    def select_node(self, node)
    def deselect_node(self, node)
    def select_node_at_position(self, position)
    def deselect_node_at_position(self, position)
    def deselect_all_nodes(self)
    def get_selected_nodes(self)
```

Control selection of nodes.

```
    
    def add_edge(self, from_node, to_node)    
    def remove_edge(self, from_node, to_node)
    
    def create_edge_from_selected_to(self, node)
    def create_edge_to_selected_from(self, node)
    
    def remove_edges_from_many(self, to_node, from_nodes)
    def remove_edges_to_many(self, from_node, to_nodes)
    
    def remove_all_node_edges(self, node)
    
    def get_edge_object(self, edge)
    def update_node_edges(self, node)
    def redraw_edges(self, node)
    def redraw_all_edges(self)

```
    
Edge management.

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
| Toggle Background      | B |


## License
GPL v2.0 - GNU General Public License Version 2

Full license text: [ [Pretty (.md)](LICENSE.md) | [Plain](LICENSE) ]