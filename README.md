# PyDeTide 


### Description
Tool for deting astronomical tide from sea level signals.
The tool is based on the 'rlowess' and 'rloess' filtering methods of the MATLAB function smooth (http://it.mathworks.com/help/curvefit/smooth.html) and it is composed by two files:

* smoothData.py: the module containing the filtering functions
* pyDeTide.py:   the main program launching a graphical user interface (GUI) for the tool


### Pre-requisites:
* numpy (to use the smoothData.py module)
* wx and matplotlib (to run the pyDeTide.py GUIand visualize your data analysis)


### Installation and run

#### Standalone tool
Download the tool, open a terminal and run:
```
$ unzip PyDeTide-xxx.zip
$ cd PyDeTide-xxx/
$ python pyDeTide.py
```
and the main frame window should appear.

Then in the file menu, you can select open file and choose a time series to analyse.
Time series have to be formatted as two-columns text files. 

#### Callable module
Alternativele, one can locally save the smoothData.py module in the PYTHON PATH and use it as any other Python module:
```
import smoothData as sd
...
s = sd.smooth(x, y, span, method)

```
where (x, y) is the time series, **span** is the number of points after and before each point of the curve used for the smoothing and **method** is one among rlowess and rloess
 


