import wxversion
wxversion.select("2.6")
import wx

import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wx import Toolbar, FigureCanvasWx,\
     FigureManager

from matplotlib.figure import Figure
from matplotlib.axes import Subplot
import matplotlib.numerix as numpy


class Plot(wx.Panel):

    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)

        self.fig = Figure((9,8), 75)
        self.canvas = FigureCanvasWx(self, -1, self.fig)
        self.toolbar = Toolbar(self.canvas)
        
        self.toolbar.Realize()

        # On Windows, default frame size behaviour is incorrect
        # you don't need this under Linux
        tw, th = self.toolbar.GetSizeTuple()
        fw, fh = self.canvas.GetSizeTuple()
        self.toolbar.SetSize(wx.Size(fw, th))

        # Create a figure manager to manage things
        self.figmgr = FigureManager(self.canvas, 1, self)
        # Now put all into a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # This way of adding to sizer allows resizing
        sizer.Add(self.canvas, 1, wx.LEFT|wx.TOP|wx.GROW)
        # Best to allow the toolbar to resize!
        sizer.Add(self.toolbar, 0, wx.GROW)
        self.SetSizer(sizer)
        self.Fit()

    def clear(self):
        a = self.fig.add_subplot(111)
        a.clear()
        
    def plot(self, data, labels = [], title = ""):
        #FIXME: what is 111?
        a = self.fig.add_subplot(111)
        a.set_title(title)
        for i in range(0, len(data)):
            d = data[i]
            if i < len(labels):
                l = labels[i]
            else:
                l = "" 
            x = map(lambda x: x[0], d)
            y = map(lambda x: x[1], d)
            a.plot(x,y, marker = None, linestyle = "-", label = l)

        if len(labels) > 0:
            a.legend(loc=2)
        a.set_xlabel("RPM")
        a.set_ylabel("Power/Torque")
        self.toolbar.update()
    def plot_sample_data(self):
        import dyno
        r = dyno.DynoRun()
        r.Load("dustin.csv")

        import smooth
        r.Smooth(smooth.NNA)
        r.Smooth(smooth.box)
        self.plot([r.torque(), r.hp()], ["Torque", "Power"])
        self.toolbar.update()

    def GetToolBar(self):
        # You will need to override GetToolBar if you are using an 
        # unmanaged toolbar in your frame
        return self.toolbar


if __name__ == "__main__":
    class testApp(wx.App):
        def OnInit(self):
                        
            self.frame = wx.Frame(None, -1, "test")
            p = Plot(self.frame, -1)
            self.SetTopWindow(self.frame)
            self.frame.Show(True)
            p.plot_sample_data()
            return True
    
    app = testApp(0)
    app.MainLoop()
