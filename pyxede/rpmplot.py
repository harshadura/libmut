############################################################################
#
# rpmplt.py
#
# Copyright 2004-6 Donour Sizemore (donour@cs.uchicago.edu)
#
# This file is part of pyXede.
#
# pyXede is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# pyXede is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyXede; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
############################################################################
#
# This wxWindows widget plots x,y coordinate data. 
#
############################################################################
import string
__version__ = string.split('$Revision: 1.5 $')[1]
__date__ = string.join(string.split('$Date: 2006/02/09 17:24:22 $')[1:3], ' ')
__author__ = ('C. Donour Sizemore <donour@cs.uchicago.edu>',)

import time

import arch
if arch.WXVERSION:
    import wxversion
    wxversion.select("2.6")

import wx
import wx.py.crust

DEFAULT_XMAX  = 8500
DEFAULT_XMIN  = 0000
DEFAULT_XSTEP = 1000
DEFAULT_XLABEL= "RPM"

DEFAULT_YMAX  = -1
DEFAULT_YMIN  = -1
DEFAULT_YSTEP = -1

DEFAULT_COLORS = [
    "BLUE",
    "RED",
    "SKY BLUE",
    "ORANGE"
    ]




class RPMPlot(wx.Panel):
    """RPMPlot is a wxWindows widget (sort of) to plot x,y coordinate
    data that is a function of vechicle RPM. Use SetData to add or set
    data points. Overhead is relatively low and should be suitable for
    frequent refresh such as realtime plotting.

    """

    def _plot(self, dc):
        """internal plot routine, this is not a public interface

        """
#        start = time.time()

        # is there anything to draw?
        if self.xmin >= self.xmax or \
           self.ymin >= self.ymax or \
           self.data == None      or \
           len(self.data) == 0:
            return

        font = wx.Font(10, wx.MODERN, wx.NORMAL,
                       wx.NORMAL, False)
        dc.SetFont(font)
        dc.BeginDrawing()

        self.offset = 40
        self.width,self.height  = self.GetClientSizeTuple() 
        self.width = self.width  - self.offset
        self.height= self.height - self.offset
         
        label_width = 50
        labels          = []
        labels_location = []
        gridlines       = []
        
        self.xscale = self.width  / float(self.xmax - self.xmin)
        self.yscale = self.height / float(self.ymax - self.ymin)

        # generate x-axis grid labels. step by label_width, start one mark
        # over so as to not label zero
        for i in range(1,self.xnum_lines+1):
            grid_pos   = i * self.xstep * self.xscale + self.offset 
            grid_label = str(i*self.xstep + self.xmin)
            labels.append(grid_label)
            labels_location.append((grid_pos, self.height))
            gridlines.append((grid_pos, self.height, grid_pos, 0))

        for i in range(1,self.ynum_lines+1):
            grid_pos   = i *self.ystep * self.yscale

            grid_label = "%3.2f" % (i*self.ystep + self.ymin )            
            if len(grid_label)>3:
                grid_label = "%3.1f" % (i*self.ystep + self.ymin )
            labels.append(grid_label)
            labels_location.append((0, self.height - grid_pos))
            gridlines.append((self.offset,  self.height - grid_pos,
                              self.width+self.offset, self.height - grid_pos))

        dc.DrawLineList(gridlines, wx.Pen("WHEAT", style = wx.SHORT_DASH))
        dc.DrawTextList(labels, labels_location,self.fg, self.bg)
        # draw axis labels
        labels = [self.xlabel]
        labels_location = [(self.width/2.0, self.height +self.offset/2)]
        dc.DrawTextList(labels, labels_location,self.fg[0:1],self.bg[0:1])

        # Build Axes
        xaxis = (self.offset, self.height, self.width+self.offset,  self.height)
        yaxis = (self.offset, self.height, self.offset,        0)
        axes = [xaxis, yaxis]
        dc.DrawLineList(axes, wx.Pen("WHITE"))        
        self._plot_points(dc,self.data)
        dc.EndDrawing()

        #        print "DrawTime: %s seconds with DrawPointList" % \
        #                         (time.time() - start)

    def _plot_points(self, dc, datain):
        self._col = 0
        def NEXT_COLOR():
            c = self.colors[self._col]
            self._col = (self._col + 1) % len(self.colors)
            return c
        # scale and flip the point data for plotting on screen

        for single_plot in datain:
            lines = []
            sp = single_plot[0] # start point
            sp = [sp[0],sp[1]]

            sp[0] = (sp[0] - self.xmin) * self.xscale
            sp[1] = (sp[1] - self.ymin) * self.yscale
            sp[1] = self.height - sp[1]
            sp[0] = sp[0] + self.offset # right

            for i in range(1, len(single_plot)):
                c = single_plot[i] # current
                c = [c[0],c[1]]
                c[0] = (c[0] - self.xmin) * self.xscale
                c[1] = (c[1] - self.ymin) * self.yscale
                c[1] = self.height - c[1]
                c[0] = c[0] + self.offset # right

                lines.append( sp+c )
                sp = c

            dc.DrawLineList(lines, wx.Pen(NEXT_COLOR(), 2))

        
    def SetData(self,data,
                xmax = DEFAULT_XMAX,xmin = DEFAULT_XMIN,xstep = DEFAULT_XSTEP,
                ymax = DEFAULT_YMAX,ymin = DEFAULT_YMIN,ystep = DEFAULT_YSTEP,
                xlabel = DEFAULT_XLABEL, xline = None,
                colors = DEFAULT_COLORS,
                ):
        """Set data points for plot. data should be a list of tuples

        """

        self.data = data

        self.xmax = xmax
        self.xmin = xmin
        self.xstep= xstep
        self.xlabel = xlabel
        self.xline  = xline

        self.ymax = ymax
        self.ymin = ymin
        self.ystep= ystep

        # default is to autoscale
        if self.ymax < 0:
            max_height = -1
            for d in data:
                max_height = max(max(map(lambda x:x[1], d)), max_height)
            self.ymax = max_height

        if self.ymin < 0:
            min_height = self.ymax
            for d in data:
                min_height = min(min(map(lambda x:x[1], d)), min_height)
            self.ymin = min_height

        if self.ystep <= 0: # no step is set
            self.ystep = (self.ymax - self.ymin) / 3
        if self.ystep == 0: # usually happens when there is no data (ymax=ymin)
            self.ystep = 1
        self.colors = colors

        self.xnum_lines = int((self.xmax - self.xmin) / self.xstep)
        self.ynum_lines = int((self.ymax - self.ymin) / self.ystep)
        
        self.fg         = [wx.NamedColor("WHITE")  ]    * (self.xnum_lines + self.ynum_lines)
        self.bg         = [wx.NamedColor("BLACK")] * (self.xnum_lines + self.ynum_lines)


        self.Refresh()
        
    def OnPaint(self, evt):
        if self.windows_refresh == 1:
            self.windows_refresh = 0

            self.Show(False)
            self.Show(True)

            dc = wx.PaintDC(self)
            dc.SetBackground(wx.Brush("BLACK"))
            dc.Clear()
            self._plot(dc)
            self.windows_refresh = 1

        elif self.windows_refresh == -1:
            dc = wx.PaintDC(self)
            dc.SetBackground(wx.Brush("BLACK"))
            dc.Clear()
            self._plot(dc)

    def Refresh(self):
        e = wx.PaintEvent()
        wx.PostEvent(self,e)

    
    def __init__(self, parent, ID = -1):
        wx.Panel.__init__(self, parent, ID)
        self.data = []

        self.windows_refresh = arch.WINDOWS_REFRESH

        self.xmax = DEFAULT_XMAX
        self.xmin = DEFAULT_XMIN
        self.xstep= 2**32 # a big number so that no grid lines are drawn

        self.ymax = DEFAULT_YMAX
        self.ymin = DEFAULT_YMIN
        self.ystep= 2**32 # a big number so that no grid lines are drawn
        wx.EVT_PAINT(self, self.OnPaint)


    def test_sin(self):
        import math, time
        p = abs(math.sin(time.time()/5.0))*10
        d = [(0,0),(5,p), (10,0)]
        self.SetData([d], xline=p,xmin = 0,xmax=10,xstep=1,ymax=10, ymin=0.0)


class PlottingPanel(wx.Panel):
    def __init__(self, parent, ID = -1):
        wx.Panel.__init__(self, parent, ID)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.power_plot = RPMPlot(self)
        self.afr_plot   = RPMPlot(self)
        self.knock_plot = RPMPlot(self)
        self.ts_plot    = RPMPlot(self)

        sizer.Add(self.power_plot, 2, wx.EXPAND)
        sizer.Add(self.afr_plot,   1, wx.EXPAND)
        sizer.Add(self.knock_plot, 1, wx.EXPAND)
        sizer.Add(self.ts_plot,    1, wx.EXPAND)

        self.SetSizer(sizer);self.SetAutoLayout(True);
        sizer.Fit(self)


    def Refresh(self):
        self.power_plot.Refresh()
        self.afr_plot.Refresh()
        self.knock_plot.Refresh()
        self.ts_plot.Refresh()

    def Update(self,run,xline = None):
        
        self.power_plot.SetData([run.torque(), run.hp()],xline=xline)
        self.afr_plot.SetData([run.afr()],colors = ["GREEN"],xline=xline)
        self.knock_plot.SetData([run.knock()],colors = ["WHITE"],xline=xline)
        self.ts_plot.SetData([run.timing_shift()],xline=xline)
        self.Refresh()


if __name__ == "__main__":
    class testApp(wx.App):
        def OnInit(self):
            tID = wx.NewId()
            
            self.frame = wx.Frame(None, -1, "pyXede")
            self.SetTopWindow(self.frame)
            self.plot = RPMPlot(self.frame)
            self.frame.Show(True)
            self.frame.SetSize((700,700))

            d = []
            for i in range(0,7500, 10):
                d.append((i,5000.0))

            self.plot.SetData([d], ymax = 7500, ystep = 500, ymin = 0)
            return True
        
            import dyno
            d = dyno.DynoRun()
            d.Load('smart_smoothed.csv')
            
            self.frame2 = wx.Frame(None, -1, "smoothed data")
            self.pp = PlottingPanel(self.frame2, -1)
            self.frame2.Show(True)

            def generate_events(plot):
                r = d
                leftover = r.data
                r.data = []
                    
                while len(leftover)>0:
                    r.data = r.data + leftover[0:32]
                    xline = r.data[-1][0]
                    leftover = leftover[32:]
                    self.pp.Update(r, xline=xline)
                    time.sleep(0.8)
                return
                import sys
                sys.exit(-1)

                while 1:
                    plot.test_sin()
                    time.sleep(0.5)

                
            import threading
            t= threading.Thread(None, generate_events, None,
                             (self.plot,))
            t.start()
            return True
        
    app = testApp(0)
    import profile
    #    profile.run("app.MainLoop()")
    app.MainLoop()



