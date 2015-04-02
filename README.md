# Pretreat
Clone this repository:
```sh
$ git clone https://github.com/fauskanger/Pretreat.git
```
## Summary
A graph editor for examining pathfinding algorithms that take tactical retreat / withdrawal options into consideration. The focus of the project will be to create an environment where agents may be required to retreat and find a suitable path planning algorithm which allows for retreats. I.e. an agent might be instructed to retreat or back up from a node during a walk along an a priori optimal path. With that in mind, this application is meant to provide the basic tools to illustrate and test such algorithms.

### Requirements
  - Math-library: Numpy [ [Official](http://www.numpy.org/) | [Wheels](http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy) ]
  - Installation package: setuptools [ [Offical](https://pypi.python.org/pypi/setuptools) ] - required by NetworkX
  - Graph library: NetworkX 1.9.1 [ [How to install](http://networkx.github.io/documentation/networkx-1.9.1/install.html) ]
  - Windowing and multimedia library: Pyglet 1.2 [ [How to install](http://www.pyglet.org/download.html) ]

### Development

  - Developed with 64-bit version of Python 3.4.2 (Kit: [Anaconda Python Package](https://store.continuum.io/cshop/anaconda/))
  - Anaconda includes the following used/required packages: (See "Requirements" above)
    - Numpy
    - setuptools
  - Tested on Windows 7 and 8
  - IDE used: JetBrain's PyCharm (Free Academic License) [ [Download here](https://www.jetbrains.com/pycharm/download/) ]

In general, http://www.lfd.uci.edu/~gohlke/pythonlibs/ is currently a great source of Python libraries. 

License
----
GPL v2.0 [ [Full license text](LICENSE.txt) ]