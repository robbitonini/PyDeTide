# PyDeTide *In Progress*


### Description
Tool for deting astronomical tide from sea level signals.
The tool is based on the 'rlowess' and 'rloess' filtering methods of the MATLAB function smooth (http://it.mathworks.com/help/curvefit/smooth.html) and it is composed by two files:

* smoothData.py: the module containing the filtering functions
* pyDeTide.py:   the main program launching a graphical user interface (GUI) for the tool


### Pre-requisites:
numpy, matplotlib (for smoothData.py module) and wx (for the pyDeTide.py GUI)


### Installation and run
Download the tool, open a terminal and run:
```
$ unzip PyDeTide-xxx.zip
$ cd PyDeTide-xxx/
$ python pyDeTide.py
```
and the main frame window should appear.

Then in the file menu, you can select open file and choose a time series to analyse.
Time series have to be formatted as two-columns text files. 


