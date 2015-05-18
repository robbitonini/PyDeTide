# PyDeTide
Tool for deting astronomical tide from sea level signals.
The tool is based on the 'rlowess' and 'rloess' filtering methods of the MATLAB function smooth (http://it.mathworks.com/help/curvefit/smooth.html) and it is composed by two files:

*smoothData.py: the module containing the filtering functions
*pyDeTide.py:   the main program launching a graphical user interface (GUI) for the tool

Pre-requisites:

numpy, matplotlib (for smoothData.py module) and wx (for the pyDeTide.py GUI)

Download the tool, then open a terminal and type:
```
$ cd PyDeTide/
$ python pyDeTide.py
```

