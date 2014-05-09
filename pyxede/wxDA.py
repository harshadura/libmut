import string
__version__ = string.split('$Revision: 1.1 $')[1]
__date__ = string.join(string.split('$Date: 2006/01/20 17:25:15 $')[1:3], ' ')
__author__ = ('C. Donour Sizemore <donour@cs.uchicago.edu>',)

import gnuplot
import arch
import csv

if arch.WXVERSION:
    import wxversion
    wxversion.select("2.6")

import wx
from wxPython.lib.mixins.listctrl import wxListCtrlAutoWidthMixin
#from wxPython.lib.filebrowsebutton import FileBrowseButton
#from wx.lib.intctrl import IntCtrl


def histogram(data, boxsize = 10):
    data.sort()
    data = map(lambda x: x - x % boxsize, data)

    points = [ ]
    for i in range(data[0], data[-1], boxsize):
        points.append( [i, 0] )
    points.append( [data[-1], 0] )
    
    for i in data:
        idx = int( (i-data[0]) / boxsize)
        points[idx][1] = points[idx][1] + 1

    result = []
    for i in points:
        if i[1] != 0:
            result.append(i)
    return result


class datalog:
    def __init__(self, filename, timecol = -1, rpmcol = -1, afrcol = -1):
        self.filename = filename
        self.data = csv.read_csv(filename)
        self.data = csv.absolve(self.data)

        self.timecol = timecol
        self.rpmcol  = rpmcol
        self.afrcol  = afrcol

    def num_chan(self):
        return len(self.data[0])
    
    def num_samples(self):
        return len(self.data)

    def RPM_data(self):
        d = map(lambda x: x[self.rpmcol], self.data)
        return d

    def AFR_data(self):
        d = map(lambda x: x[self.afrcol], self.data)
        return d

class MyListCtrl(wx.ListCtrl, wxListCtrlAutoWidthMixin):
    def __init__(self, parent, id, pos = wx.DefaultPosition,
                 size = wx.DefaultSize, style = 0):
        wx.ListCtrl.__init__(self,parent,id,pos,size,style)
        wxListCtrlAutoWidthMixin.__init__(self)  

class DAPanel(wx.Panel):
    
    def __init__(self, parent, ID = -1):
        # A border is needed to keep OSX widgets from looking retarded.
        BORDERSIZE = 5
        wx.Panel.__init__(self, parent, ID)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.log = datalog("to_campus.csv", 0, 1)

        stats = []
        stats.append(("Source file:", self.log.filename) )
        stats.append(("Number of Samples:", self.log.num_samples()))
        stats.append(("Number of Channels:", self.log.num_chan()))
        stats.append(("Max RPM", max(self.log.RPM_data())))
        
        
        nb = self.DANB(self)
        sp = self.StatPanel(nb)
        sp.Set(stats)
        cpp = self.CommonPlotPanel(nb, data = self.log)
        nb.AddPage(sp, "Stats")
        nb.AddPage(cpp, "Common Plots")

        sizer.Add(nb, flag=wx.ALL,border=BORDERSIZE)
        self.SetSizer(sizer);self.SetAutoLayout(True);sizer.Fit(self)

        def OnSelfSize(e, win = self):
            w,h =  self.GetClientSizeTuple()
            nb.SetSize((w - 2*BORDERSIZE,h-2*BORDERSIZE))
        wx.EVT_SIZE(self, OnSelfSize)
    # __end init _____________________________________________________________


    class CommonPlotPanel(wx.Panel):
         def __init__(self, parent, ID = -1, data = None):
            wx.Panel.__init__(self, parent, ID)
            sizer = wx.BoxSizer(wx.VERTICAL)                

            hist_sizer = wx.BoxSizer(wx.HORIZONTAL)
            bid = wx.NewId()
            rpm_hist_but = wx.Button(self, bid, "RPM Histogram") 
            hist_sizer.Add(rpm_hist_but)
            self.hist_slider = wx.Slider(self, -1, value = 5,
                                    minValue=1, maxValue=1000)
            hist_sizer.Add(self.hist_slider)

            def histogram_plot(evt = None):
                d = data.RPM_data()
                bs = self.hist_slider.GetValue()
                h = histogram(d, boxsize = bs)
                gnuplot.plot([h])
            wx.EVT_BUTTON(self, bid, histogram_plot)

            sizer.Add(hist_sizer)

            xy_sizer = wx.BoxSizer(wx.HORIZONTAL)
            bid = wx.NewId()
            xy_but = wx.Button(self, bid, "2D Plot") 
            hist_sizer.Add(xy_but)
            sizer.Add(xy_sizer)
            
            self.SetSizer(sizer);self.SetAutoLayout(True);sizer.Fit(self)
                        
    # ________________________________________________________________________
    class StatPanel(wx.Panel):
        def __init__(self, parent, ID = -1):
            wx.Panel.__init__(self, parent, ID)
            self.list = MyListCtrl(self,-1,
                                        style =
                                        wx.LC_REPORT     |
                                        wx.LC_HRULES     |
                                        wx.LC_SINGLE_SEL )
            self.list.InsertColumn(0, "", width=100)
            self.list.InsertColumn(1, "", width=100)
            
            def OnSelfSize(e, win = self):
                w,h =  self.GetClientSizeTuple()
                self.list.SetSize(self.GetSize())
                self.list.SetDimensions(0,0,w,h)
            wx.EVT_SIZE(self, OnSelfSize)
            
        def Set(self,data):
            for i in range(0, len(data)):
                elt = data[i]
                if len(elt) < 2:
                    raise ValueError, "Improper statistic data"
                else:
                    self.list.InsertStringItem(i, str(elt[0]) )
                    self.list.SetStringItem(i, 1, str(elt[1]) )
    # _end stat panel ________________________________________________________
               
    class DANB(wx.Notebook):
        def __init__(self, parent, ID = -1):
            wx.Notebook.__init__(self,parent,ID)
    # _end notebook __________________________________________________________


class wxDA(wx.Frame):
    def __init__(self,parent, title):
        wx.Frame.__init__(self,parent, -1, title)
        panel = DAPanel(self)

#        def OnPSize(e, win = panel):
#            panel.SetSize(e.GetSize())
          #  w,h = panel.GetClientSizeTuple()
         #   panel.box_title.SetSize(e.GetSize())
         #   panel.box_title.SetDimensions(0, 0, w, h)
#        wx.EVT_SIZE(panel, OnPSize)
                                                             

        self.Show(True)
        return
    
if __name__ == "__main__":
    class testApp(wx.App):
        def OnInit(self):
            tID = wx.NewId()
            
            self.frame = wxDA(None, "wxDA Test")
            self.SetTopWindow(self.frame)
            self.frame.Show(True)
            return True


    app = testApp(0)
    app.MainLoop()

    def go():
        dl =datalog("homie.csv", 0, 1, 5)
    
        h = histogram(dl.RPM_data(), boxsize=2)
        gnuplot.plot([h])
            

    #import profile
    #profile.run("go()")
   # go()
