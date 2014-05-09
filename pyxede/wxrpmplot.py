import wxversion
wxversion.select("2.6")

import wx
from wx.lib.plot import *

class RPMPlot(wx.Panel):
    def __init__(self, parent, id = -1):
        wx.Panel.__init__(self,parent, id)

        self.canvas = PlotCanvas(parent)
        
    def draw(self, runs):
        lines = []
        
        for i in range(0, len(runs)):
            r = runs[i]
            t = r.torque()
            lines.append( PolyLine(t,legend='Torque %d' % i, colour="blue"))
            p = r.hp()
            lines.append( PolyLine(p,legend='Power %d' % i, colour="red") )
        g = PlotGraphics(lines,"df", "X Axis", "Y Axis")
        self.canvas.Draw(g)

if __name__ == "__main__":
    class testApp(wx.App):
        def OnInit(self):
            tID = wx.NewId()
            
            self.frame = wx.Frame(None, -1, "test")
#            self.p = RPMPlot(self.frame, -1)
            self.SetTopWindow(self.frame)

#            self.acanvas = PlotCanvas(self.frame)
            self.canvas = PlotCanvas(self.frame)
            def draw(runs):
                lines = []
                
                for i in range(0, len(runs)):
                    r = runs[i]
                    t = r.torque()
                    lines.append( PolyLine(t,legend='Torque %d' % i, colour="blue"))
                    p = r.hp()
                    lines.append( PolyLine(p,legend='Power %d' % i, colour="red") )
                    g = PlotGraphics(lines,"df", "X Axis", "Y Axis")
                self.canvas.Draw(g)

            def plot(e = None):
                import dyno
                d = dyno.DynoRun()
                d.Load("dustin.csv")
                d1 = dyno.DynoRun()
                d1.Load("dustin.csv")
                draw([d,d1])
    

            self.mainmenu = wx.MenuBar()
            menu = wx.Menu()
            menu.Append(200, 'plot')
            self.Bind(wx.EVT_MENU, plot, id=200)
            self.mainmenu.Append(menu, 'File')
            
            self.frame.SetMenuBar(self.mainmenu)
            
            self.frame.Show(True)
            self.frame.SetSize((300,300))

    
           
            return True
        
    app = testApp(0)
    app.MainLoop()

