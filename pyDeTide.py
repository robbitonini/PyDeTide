#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

import os
import sys
import wx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as figcv
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as navtb
import smoothData as sd


mpl.rcParams['xtick.direction']='out'
mpl.rcParams['ytick.direction']='out'
mpl.rcParams['axes.labelsize']='12'
mpl.rcParams['xtick.labelsize']='12'
mpl.rcParams['ytick.labelsize']='12'
mpl.rcParams['legend.fontsize']='12'
mpl.rcParams['font.family']='serif'
mpl.rcParams['font.sans-serif']='Times'


class newTab(wx.Panel):
  """
  Create a new Tab in the main window with the canvas area
  and the plotted data. Called by loadData method in AppFrame Class.  
  """
  def __init__(self, parent):
    wx.Panel.__init__(self, parent)
    self.fig = plt.figure()
    self.fig.clf()
    self.canvas = figcv(self, -1, self.fig)
    self.canvas.SetSize(self.GetSize())
    self.canvas.draw()
    vboxTab = wx.BoxSizer(orient=wx.VERTICAL)
    vboxTab.Add(self.canvas, 1, wx.EXPAND|wx.ALL, 0)
    self.toolbar = navtb(self.canvas)
    vboxTab.Add(self.toolbar, 0, wx.EXPAND, 0)
    self.SetSizer(vboxTab)


  def plotData(self, *kargs):
    """
    Plot the data creating two sub-figures in the canvas.
    """

    d = kargs[0]    
    self.x = d[:,0]
    self.y = d[:,1]
    sp = kargs[1]
    me = kargs[2]
    fig2 = str(kargs[3])
    s = sd.smooth(self.x, self.y, sp, me)
    self.res = self.y-s
    self.fig.clf()
    self.fig.subplots_adjust(left=None, bottom=None, right=None, 
                             top=None, wspace=None, hspace=0.3)
    self.fig.hold(True)
    ax1 = plt.subplot(2,1,1)
    plt.plot(self.x, self.y, color="#000000", linewidth=1.5)
    plt.plot(self.x, s, color="#ff0000", linewidth=1.5, label="Filter ("+str(me)+")")
    plt.grid(True)
    plt.xlim(min(self.x), max(self.x))
    plt.ylabel(r"Sea level (m)")
    plt.legend(loc='lower right', bbox_to_anchor=(0.5, 0.99))
    
    ax2 = plt.subplot(2,1,2, sharex=ax1)
    plt.hold(True)
    if (fig2 == "Res"):
      plt.plot(self.x, self.res, color="#0000ff", linewidth=1.5)
      plt.axhline(y=0, color="#999999")
      plt.ylim(min(self.res), max(self.res))
      plt.ylabel(r"Residual (m)")
      #plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
    elif (fig2 == "Spe"):
      plt.specgram(self.y, NFFT=256, Fs=2, Fc=0, noverlap=128,
                   cmap=plt.cm.jet, xextent=(min(self.x),max(self.x)), 
                   pad_to=None, sides='default', scale_by_freq=True, 
                   mode='psd', scale='dB')
      plt.ylabel(r"Power Spectral Density")

    plt.xlim(min(self.x), max(self.x))
    plt.grid(True)
    plt.xlabel(r"Time (min)")
    wx.Yield()
    self.canvas.draw()
    self.Layout()
    
    

class AppFrame(wx.Frame):
  """
  Main window frame of PyDeTide software.
  
  """
  
  span = 15
  methods = ["rloess", "loess"]
  method = methods[0]
  subfig2 = "Res"
  
  def __init__(self, parent, id, title):
    wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition)
    #self.SetIcon(wx.Icon("icons/", wx.BITMAP_TYPE_ANY))

    self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, 
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
    # menubar
    self.menuBar = wx.MenuBar()
    self.fileMenu = wx.Menu()

    loadItem = wx.MenuItem(self.fileMenu, 102, '&Load Data')
    #quit_item.SetBitmap(wx.Bitmap('icons/exit.png'))
    self.fileMenu.AppendItem(loadItem)
    self.Bind(wx.EVT_MENU, self.loadData, id=102)
    self.fileMenu.AppendSeparator()

    self.exportItem = wx.MenuItem(self.fileMenu, 103, '&Export as text file')
    self.Bind(wx.EVT_MENU, self.exportXYZfile, id=103)
    self.fileMenu.AppendItem(self.exportItem)
    self.exportItem.Enable(False)

    quitItem = wx.MenuItem(self.fileMenu, 105,  '&Quit')
    self.fileMenu.AppendItem(quitItem)
    self.Bind(wx.EVT_MENU, self.onQuit, id=105)

    self.menuBar.Append(self.fileMenu, '&File')

    self.SetMenuBar(self.menuBar)

    # main sizer
    hbox = wx.BoxSizer(orient=wx.HORIZONTAL)
    
    # left panel   
    self.pnlLT = wx.Panel(self, wx.ID_ANY)

    vboxLT = wx.BoxSizer(orient=wx.VERTICAL)

    hboxSmooth = wx.StaticBoxSizer(wx.StaticBox(self.pnlLT, wx.ID_ANY, 
                                 'Smoothing'), orient=wx.VERTICAL)
    # box span
    hboxSpan = wx.BoxSizer(orient=wx.HORIZONTAL)
    hboxSpan.Add(wx.StaticText(self.pnlLT, wx.ID_ANY, "Span: ", 
                               size=(-1,26)), 0, wx.TOP, 8)
    self.tSpan = wx.TextCtrl(self.pnlLT, wx.ID_ANY, size=(40,24))
    self.tSpan.SetValue(str(self.span))
    hboxSpan.Add(self.tSpan, 0, wx.LEFT|wx.TOP, 2)
    hboxSmooth.Add(hboxSpan, 0, wx.LEFT|wx.RIGHT|wx.TOP, 10)
    
    # box method
    hboxMet = wx.BoxSizer(orient=wx.HORIZONTAL)
    hboxMet.Add(wx.StaticText(self.pnlLT, wx.ID_ANY, "Method: ", 
                              size=(-1,26)), 0, wx.TOP, 12)
    self.cMet = wx.ComboBox(self.pnlLT, wx.ID_ANY, choices = self.methods, 
                                  style = wx.CB_READONLY, size=(-1,24))
    self.cMet.SetSelection(0)
    hboxMet.Add(self.cMet, 0, wx.LEFT|wx.TOP, 4)
    self.Bind(wx.EVT_COMBOBOX, self.selMethod, self.cMet)
    hboxSmooth.Add(hboxMet, 0, wx.LEFT|wx.RIGHT, 10)

    # box update
    hboxUpdate = wx.BoxSizer(orient=wx.HORIZONTAL)
    self.bSpan = wx.Button(self.pnlLT, wx.ID_ANY, 
                           'Update Plot', size=(-1,26))
    hboxUpdate.Add(self.bSpan, 0, wx.ALIGN_BOTTOM|wx.LEFT, 4)
    self.Bind(wx.EVT_BUTTON, self.selSpan, self.bSpan)
    hboxSmooth.Add(hboxUpdate, 0, wx.ALL, 10)

    vboxLT.Add(hboxSmooth)
    

    self.rb1 = wx.RadioButton(self.pnlLT, wx.ID_ANY, 'Residuals', style=wx.RB_GROUP)
    self.rb2 = wx.RadioButton(self.pnlLT, wx.ID_ANY, 'Spectrogram')
    self.Bind(wx.EVT_RADIOBUTTON, self.selSubFig2, self.rb1)
    self.Bind(wx.EVT_RADIOBUTTON, self.selSubFig2, self.rb2)
    vboxLT.Add(self.rb1, 0, wx.TOP, 12)
    vboxLT.Add(self.rb2, 0, wx.BOTTOM, 6)


    hboxSpectra = wx.StaticBoxSizer(wx.StaticBox(self.pnlLT, wx.ID_ANY, 
                                 'Spectrogram'), orient=wx.VERTICAL)

    vboxLT.Add(hboxSpectra)

    self.pnlLT.SetSizer(vboxLT)
    self.pnlLT.Enable(False)
    
    hbox.Add(self.pnlLT, 0, wx.EXPAND|wx.ALL, 10)

    # right panel
    self.pnlRT = wx.Panel(self)

    vboxRT = wx.BoxSizer(orient=wx.VERTICAL)
    self.nb = wx.Notebook(self.pnlRT)

    vboxRT.Add(self.nb, 1, wx.EXPAND|wx.ALL, 0)
    self.pnlRT.SetSizer(vboxRT)
    
    hbox.Add(self.pnlRT, 1, wx.EXPAND|wx.ALL, 5)

    self.Bind(wx.EVT_CLOSE, self.onQuit)
    self.sb = self.CreateStatusBar()
    self.sb.SetStatusText("No data loaded")
    self.SetSizer(hbox)
    self.SetSize((850,650))
    self.Centre()
    

  def loadData(self, event):
    """
    """
    dflDir = os.path.expanduser("~")
    dlg = wx.FileDialog(self, message="Upload File", defaultDir=dflDir, 
                        defaultFile="", wildcard="*.*", 
                        style=wx.FD_OPEN|wx.FD_CHANGE_DIR)
    
    if (dlg.ShowModal() == wx.ID_OK):
      path = dlg.GetPath()

    else:
      msg = "WARNING\nYou have NOT selected any file"
      dlg = wx.MessageDialog(self, msg, "WARNING", wx.OK|wx.ICON_WARNING)
      dlg.ShowModal()
      dlg.Destroy()
      path = ""

    title = os.path.basename(path)
    dlg.Destroy()
    self.pnlLT.Enable(True)
    self.pnTab = newTab(self.nb)
    self.nb.AddPage(self.pnTab, title)
    self.data = np.loadtxt(path)
    self.pnTab.plotData(self.data, self.span, self.method, self.subfig2)
    self.sb.SetStatusText("Data loaded!")
    self.exportItem.Enable(True)


  def onQuit(self, event):
    """
    Quit the tool. Bye!
    """
    self.Destroy()
    sys.exit(0)


  def selSubFig2(self, event):
    """
    """
    if self.rb1.GetValue():
      self.subfig2 = "Res"
    elif self.rb2.GetValue():
      self.subfig2 = "Spe"
    self.pnTab.plotData(self.data, self.span, self.method, self.subfig2)
      

  def selSpan(self, event):
    """
    Selection of the span value.
    """
    self.span = float(self.tSpan.GetValue())
    self.pnTab.plotData(self.data, self.span, self.method, self.subfig2)
    self.Layout()


  def selMethod(self, event):
    """
    Selection of the smoothing method.
    """
    self.method = self.cMet.GetValue()
    self.pnTab.plotData(self.data, self.span, self.method, self.subfig2)
    self.Layout()


  #def plotData(self, *kargs):
    #"""
    #It plots hazard curves.
  
    #"""
    
    #d = kargs[0]    
    #self.x = d[:,0]
    #self.y = d[:,1]
    #sp = kargs[1]
    #me = kargs[2]
    #s = sd.smooth(self.x, self.y, sp, me)
    #self.res = self.y-s

    #self.fig.clf()
    #self.fig.subplots_adjust(left=None, bottom=None, right=None, 
                             #top=None, wspace=None, hspace=0.3)
    #self.fig.hold(True)
    #plt.subplot(2,1,1)
    #plt.plot(self.x, self.y, color="#000000", linewidth=1, label="Observed")
    #plt.plot(self.x, s, color="#ff0000", linewidth=1, label="Filtered")
    #plt.grid(True)
    #plt.ylabel("Sea level (m)")
    #plt.legend()
    
    #plt.subplot(2,1,2)
    #plt.hold(True)
    #plt.plot(self.x, self.res, color="#0000ff", linewidth=1)
    #plt.axhline(y=0, color="#666666")
    #plt.ylim(min(self.res), max(self.res))
    #plt.grid(True)
    #plt.xlabel("Time (min)")
    #plt.ylabel("Residual (m)")

    #self.sb.SetStatusText("Data loaded!")
    #self.canvas.draw()
    #self.Layout()


  def exportXYZfile(self, event):
    """
    Export ascii text file: 3 columnx with x,y,res 
    """
    
    ext = ".txt"
    dflDir = os.path.expanduser("~")
    dlg = wx.FileDialog(self, message="Save File as...", 
                        defaultDir=dflDir, defaultFile="*.txt", 
                        wildcard="*.*", style=wx.SAVE|wx.FD_OVERWRITE_PROMPT)

    if (dlg.ShowModal() == wx.ID_OK):
      savepath = dlg.GetPath()
      if (savepath[-4:] == ext):
        filename = savepath
      else:
        filename = savepath + ext
        
      fp = open(filename, "w")
      for i in range(len(self.x)):
        fp.write("{0} {1} {2} \n".format(self.x[i], self.y[i], self.res[i]))

      fp.close()

    else:
      msg = "WARNING\nYou have NOT selected any file"
      dlg = wx.MessageDialog(self, msg, "WARNING", wx.OK|wx.ICON_WARNING)
      dlg.ShowModal()
      path = ""
    
    dlg.Destroy()


class AppGui(wx.App):
  """
  Instance of the main GUI class 
  """
  def OnInit(self):
    frame = AppFrame(None, -1, "PyDeTide")
    frame.Show(True)
    self.SetTopWindow(frame)
    frame.Centre()
    return True


# starting the main gui
if __name__ == "__main__":
  app = AppGui(0)
  app.MainLoop()
