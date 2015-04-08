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
The above is used to improve autocompletion in PyCharm, so that it will suggest attributes from `self.bar` relevant to the known type.
This is not only used in `__init__`, but the hidden type of `bar` is an example of motivation.

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
| Set Start | S + LMB| S, then LMB |
| Set Destination | D + LMB| D, then LMB |
| Complete Search\*      | Space |

\*) Applicable when pathfinding algorithm is illustrated step by step.

### Miscellaneous
| Event         | Input         |
| :------------- |:-------------|
| Generate Grid of Nodes      | G |
| Toggle Background      | B |


## License
GPL v2.0 - GNU General Public License Version 2

Full license text: [ [Pretty (.md)](LICENSE.md) | [Plain](LICENSE) ]