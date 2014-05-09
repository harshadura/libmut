############################################################################
#
# wxdyno.py
#
# Copyright 2005 Donour Sizemore (donour@cs.uchicago.edu)
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

import string
__version__ = string.split('$Revision: 1.6 $')[1]
__date__ = string.join(string.split('$Date: 2006/01/20 17:25:15 $')[1:3], ' ')
__author__ = ('C. Donour Sizemore <donour@cs.uchicago.edu>',)


import os

import dyno
import smooth
import gnuplot
# FIXME: gnuplot terminal types need to be centrally managed
import arch
import rpmplot

if arch.WXVERSION:
    import wxversion
    wxversion.select("2.6")

import wx
from wxPython.lib.mixins.listctrl import wxListCtrlAutoWidthMixin
from wxPython.lib.filebrowsebutton import FileBrowseButton
from wx.lib.intctrl import IntCtrl

DYNOFILETYPES = "Pyxede Dyno Runs (*.csv)|*.csv|" \
                "All Files|*.*"

def FileError(parent, mesg):
    error_dlg = wx.MessageDialog(parent,mesg,"File Error",
                                wx.OK | wx.ICON_INFORMATION)
    error_dlg.ShowModal()

class DynoList(wx.Frame):
    class MyListCtrl(wx.ListCtrl, wxListCtrlAutoWidthMixin):
        def __init__(self, parent, id, pos = wx.DefaultPosition,
                     size = wx.DefaultSize, style = 0):
            wx.ListCtrl.__init__(self,parent,id,pos,size,style)
            wxListCtrlAutoWidthMixin.__init__(self)    

    class GnuplotDialog(wx.Dialog):
        def __init__(self, parent, ID, title = "Plot with Gnuplot", 
                     pos = wx.DefaultPosition,
                     size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE):
            pre = wx.PreDialog()
            pre.Create(parent, ID, title, pos, size, style)
            self.this = pre.this
              
            sizer = wx.BoxSizer(wx.VERTICAL)
            
            # Controls        
            run_select = wx.BoxSizer(wx.HORIZONTAL)

            sourcelist=map(lambda x: "Run #%d" % x,range(0, len(parent.runs)))
            self.runlist = wx.ListBox(self, -1, size = (100, 200),
                                      choices = sourcelist)
            self.runlist.SetSelection(0)
            run_select.Add(self.runlist, 5,5)

            bID = wx.NewId()
            buttons = wx.BoxSizer(wx.VERTICAL)
            add_btn = wx.Button(self,bID, "Add ->")
            buttons.Add(add_btn, 5,5)
            rem_btn = wx.Button(self,bID+1, "Clear --")            
            buttons.Add(rem_btn, 5,5)
            run_select.Add(buttons, 10, 0)

            self.selectlist = wx.ListBox(self, -1, size = (100,200))
            run_select.Add(self.selectlist, 5,5)

            sizer.AddSizer(run_select, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

            self.selected = []
            def add(evt):
                sel = self.runlist.GetSelection()
                if sel >= 0:
                    self.selected.append(sel)
                    # FIXME: it would be better to do a binary
                    #        search then insert 
                    self.selected.sort()
                    #FIXME: remove duplicates
                    sel_list = map(lambda x: "Run #%d" % x, self.selected)
                    self.selectlist.Set(sel_list)
                
 
            def rem(evt):
                self.selected = []
                self.selectlist.Set(self.selected)
                
            wx.EVT_BUTTON(self, bID,   add)
            wx.EVT_BUTTON(self, bID+1, rem)
            wx.EVT_LISTBOX_DCLICK(self.runlist, -1, add)

            def set_term_txt(event):
                arch.SetGnuplotTerminal(event.GetString())
            def set_term_box(event):
                arch.SetGnuplotTerminal(event.GetString())
            box = wx.BoxSizer(wx.HORIZONTAL)
            txt = wx.StaticText(self, -1, "Format ")
            box.Add(txt, 0, wx.EAST | wx.WEST | wx.EXPAND, 0)
            cID = wx.NewId()
            cb = wx.ComboBox(self, cID, arch.GNUPLOT_TERMINAL,
                             choices = arch.GNUPLOT_TERMINALS)
            box.Add(cb, 1, wx.EAST | wx.WEST | wx.EXPAND, 0)
            sizer.Add(box, 0, wx.EAST | wx.WEST | wx.EXPAND, 0)
            wx.EVT_TEXT(    self, cID, set_term_txt)
            wx.EVT_COMBOBOX(self, cID, set_term_box)

            def fbbo_callback(event):
                arch.GNUPLOT_OUTPUT = event.GetString()

            fbbo = FileBrowseButton(self,-1,initialValue = arch.GNUPLOT_OUTPUT,
                                changeCallback = fbbo_callback)
            fbbo.SetLabel("Output:")
            sizer.Add(fbbo, 1, wx.EAST | wx.WEST | wx.EXPAND, 5)


            box = wx.BoxSizer(wx.HORIZONTAL)
            
            box.Add(wx.Button(self, wx.ID_OK, "Plot"), 0 ,
                    wx.ALIGN_CENTRE|wx.ALL, 5),
            box.Add(wx.Button(self, wx.ID_CANCEL, "Cancel"), 0 ,
                    wx.ALIGN_CENTRE|wx.ALL, 5),
            sizer.AddSizer(box, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
                
            self.SetSizer(sizer);self.SetAutoLayout(True); sizer.Fit(self)


    #__ end of GnuplotDialog __________________________________________________
    def __init__(self, parent, title):
        wx.Frame.__init__(self,parent, -1, title)

        splitter = wx.SplitterWindow(self, -1)
        self.plot        = rpmplot.PlottingPanel(splitter, -1)
        
        self.runs     = []  # list of loaded dyno runs
        self.selected = -1  
        self.viewing  = {}  # dictionary of currently viewed data
        
        self.mainmenu = wx.MenuBar()
        menu = wx.Menu()
        menu.Append(200, 'View')
        self.Bind(wx.EVT_MENU, self.ViewDynoData, id=200)

        trimmenu = wx.Menu()
        ID = 2011
        trimmenu.Append(ID, "Above Torque Threshold", '')
        self.Bind(wx.EVT_MENU, self.trim_threshold, id = 2011)
        i = 2
        while i<=256:
            ID = 2010+i
            def t(evt):
                n = evt.GetId()-2010
                self.trim(n)
            trimmenu.Append(ID, "Trim %.3d points" % i, '')
            self.Bind(wx.EVT_MENU, t, id = ID)
            i = i*2
        menu.AppendMenu(2010, "Trim",trimmenu) 

        menu.AppendSeparator()
        menu.Append(202, 'Load\tCtrl+o', 'Load dyno run from file')
        self.Bind(wx.EVT_MENU, self.LoadDyno, id=202)
        menu.Append(203, 'Save\tCtrl+s', 'Save dyno run to file')
        self.Bind(wx.EVT_MENU, self.SaveDyno, id=203)
        menu.AppendSeparator()
        menu.Append(204, 'Import\tCtrl+i', '')
        self.Bind(wx.EVT_MENU, self.ImportDyno, id=204)
        menu.AppendSeparator()
        menu.Append(205, 'Hide window\tCtrl+w')
        self.Bind(wx.EVT_MENU, self.Hide, id=205)
        self.mainmenu.Append(menu, 'Data')

        menu = wx.Menu()
        menu.Append(300, 'Gnuplot', 'Plot with gnuplot')
        self.Bind(wx.EVT_MENU, self.gnuplot_manual, id=300)
        smoothmenu = wx.Menu()
        smoothmenu.Append(3020, 'Savgol (recommended)')
        self.Bind(wx.EVT_MENU, self.SmoothSavGol, id=3020)
        smoothmenu.Append(3021, 'Box')
        self.Bind(wx.EVT_MENU, self.SmoothBox, id=3021)
        smoothmenu.Append(3022, 'Running Average')
        self.Bind(wx.EVT_MENU, self.SmoothRA, id=3022)

        nnamenu = wx.Menu()
        i = 2
        while i<=256:
            ID = 30230+i
            def t(evt):
                n = evt.GetId()-30230
                self.SmoothNNA(n)            
            nnamenu.Append(ID, "Window %.3d points" % i, '')
            self.Bind(wx.EVT_MENU, t, id=ID)
            i = i*2

        smoothmenu.AppendMenu(30230, 'NNA', nnamenu)
        
        menu.AppendMenu(302, 'Smooth', smoothmenu)

        self.mainmenu.Append(menu, 'Analysis')
        
        self.SetMenuBar(self.mainmenu)

        self.mainmenu.Enable(203, 0)
        self.mainmenu.Enable(300, 0)
        self.mainmenu.Enable(302, 0)

        panel = wx.Panel(splitter,-1)
        self.list = self.MyListCtrl(panel,-1,
                                    style =
                                    wx.LC_REPORT     |
                                    wx.LC_HRULES     |
                                    wx.LC_SINGLE_SEL )

        self.list.InsertColumn(0, "Runs", width=100)
        self.list.InsertColumn(1, "Max Torque", width=100)
        self.list.InsertColumn(2, "Torque Area", width=100)
        self.list.InsertColumn(3, "Max Power", width=100)
        self.list.InsertColumn(4, "Power Area", width=100)
        self.list.InsertColumn(5, "Lean Max", width=100)
        
        def ListSel(evt):
            self.selected = evt.m_itemIndex
            self.plot_run()
        self.Bind(wx.EVT_LIST_ITEM_SELECTED,ListSel, self.list)

        def ListAct(evt):
            self.selected = evt.m_itemIndex
            self.plot_seperate()
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED,ListAct, self.list)

        def OnPSize(e, win = panel):
            panel.SetSize(e.GetSize())
            w,h = panel.GetClientSizeTuple()
            self.list.SetSize(e.GetSize())
            self.list.SetDimensions(0, 0, w, h)
        wx.EVT_SIZE(panel, OnPSize)

        # Hide the window when user closes it
        def OnClose(event):
            if event.CanVeto():
                self.Show(False)
                event.Veto()

        wx.EVT_CLOSE(self, OnClose)

        self.SetSize((600,600))
        splitter.SplitHorizontally(panel, self.plot, 200)

#        self.Show(True)

#        data = dyno.read_csv("UTEC.csv")
#        d = dyno.DynoRun()
#        d.Import(data, 0,sample_rate = 5, afr_col=12)
#        self.AddRun(d)

#        data = dyno.read_csv("smart2.csv")
#        d = dyno.DynoRun()
#        d.Import(data, 1,time_col = 0, afr_col=3, knock_col=2,ts_col=10)
#        self.AddRun(d)

    #__________________________________________________________________________
    def Hide(self, e = None):
        self.Show(False)
    #__________________________________________________________________________
    def ImportDyno(self, e = None):
        class ImportDialog(wx.Dialog):
            def __init__(self, parent, ID, title, data,
                         pos = wx.DefaultPosition,
                         size = wx.DefaultSize,
                         style =wx.SYSTEM_MENU|wx.RESIZE_BORDER):
                pre = wx.PreDialog()
                pre.Create(parent, ID, title, pos, size, style)
                self.this = pre.this
                sizer = wx.BoxSizer(wx.VERTICAL)

                panel1 = wx.Panel(self, -1)
                panel1.SetAutoLayout(True)
                
                self.sample_data = parent.MyListCtrl(panel1,-1,
                                                   style =
                                                   wx.LC_REPORT     |
                                                   wx.LC_HRULES     |
                                                   wx.LC_SINGLE_SEL )

                num_col = len(data[0])

                for i in range(0, num_col):
                    self.sample_data.InsertColumn(i, "Col %d" % i)

                for i in range(0,5):
                    self.sample_data.InsertStringItem(i,str(data[i][0]))
                    for j in range(0, num_col):
                        self.sample_data.SetStringItem(i, j,str(data[i][j]))

                sizer.Add(panel1, 1,wx.EXPAND,0)               
                def OnPSize(e, win = panel1):
                    self.sample_data.SetSize(panel1.GetSize())
                wx.EVT_SIZE(panel1, OnPSize)

                ctrlsizer = wx.BoxSizer(wx.HORIZONTAL)
                
                col1 = wx.BoxSizer(wx.VERTICAL)
                
                rsizer = wx.BoxSizer(wx.HORIZONTAL)
                self.rpm = wx.Choice(self,-1,
                                     choices = map(str,range(0,num_col)))
                self.rpm.SetSelection(0)
                rsizer.Add(self.rpm,0,0,0)
                txt = wx.StaticText(self,-1, "RPM Column")
                rsizer.Add(txt,0,wx.WEST,5)
                col1.Add(rsizer,0,wx.SOUTH,5)

                rsizer = wx.BoxSizer(wx.HORIZONTAL)
                self.afr = wx.Choice(self,-1,
                                     choices = map(str,range(0,num_col)))
                self.afr.SetSelection(0)
                rsizer.Add(self.afr,0,0,0)
                txt = wx.StaticText(self,-1, "Wideband A/F:")
                rsizer.Add(txt,0,wx.WEST,5)
                col1.Add(rsizer,0,wx.SOUTH,5)

                rsizer = wx.BoxSizer(wx.HORIZONTAL)
                self.knock = wx.Choice(self,-1,
                                     choices = map(str,range(0,num_col)))
                self.knock.SetSelection(0)
                rsizer.Add(self.knock,0,0,0)
                txt = wx.StaticText(self,-1, "Knock:")
                rsizer.Add(txt,0,wx.WEST,5)
                col1.Add(rsizer,0,wx.SOUTH,5)

                rsizer = wx.BoxSizer(wx.HORIZONTAL)
                self.ts = wx.Choice(self,-1,
                                     choices = map(str,range(0,num_col)))
                self.ts.SetSelection(0)
                rsizer.Add(self.ts,0,0,0)
                txt = wx.StaticText(self,-1, "TimingShift:")
                rsizer.Add(txt,0,wx.WEST,5)
                col1.Add(rsizer,0,wx.SOUTH,5)

                col2 = wx.BoxSizer(wx.VERTICAL)
                # Time source selection
                time_box_title = wx.StaticBox(self,-1, "Power Calculation")
                time_box = wx.StaticBoxSizer(time_box_title,wx.VERTICAL)
                tb       = wx.FlexGridSizer(0,2,0,0)
                
                self.tsfd_radio = wx.RadioButton(self, -1, " Timestamp from data ")
                self.sr_radio   = wx.RadioButton(self, -1, " Samplerate ")
                self.tfd_radio  = wx.RadioButton(self, -1, " Torque from data ")
                self.pfd_radio  = wx.RadioButton(self, -1, " Power from data ")
                self.pfd_radio.Enable(False)
                self.time_ctrl1 = wx.Choice(self,-1,
                                       choices = map(str,range(0,num_col)))
                self.time_ctrl1.SetSelection(0)
                self.time_ctrl2 = IntCtrl(self,-1)
                self.time_ctrl2.Enable(False)

                self.torque_ctrl = wx.Choice(self,-1,
                                       choices = map(str,range(0,num_col)))
                self.torque_ctrl.Enable(False)
                self.power_ctrl = wx.Choice(self,-1,
                                       choices = map(str,range(0,num_col)))
                self.power_ctrl.Enable(False)

                tb.Add(self.tsfd_radio,  1,wx.EAST|wx.NORTH|wx.SOUTH,4)
                tb.Add(self.time_ctrl1,  1,wx.WEST|wx.NORTH|wx.SOUTH,4)
                tb.Add(self.sr_radio,    1,wx.EAST|wx.NORTH|wx.SOUTH,4)
                tb.Add(self.time_ctrl2,  1,wx.WEST|wx.NORTH|wx.SOUTH,4)

                tb.Add(self.tfd_radio,    1,wx.EAST|wx.NORTH|wx.SOUTH,4)
                tb.Add(self.torque_ctrl,  1,wx.WEST|wx.NORTH|wx.SOUTH,4)
                tb.Add(self.pfd_radio,    1,wx.EAST|wx.NORTH|wx.SOUTH,4)
                tb.Add(self.power_ctrl,   1,wx.WEST|wx.NORTH|wx.SOUTH,4)

                time_box.Add(tb,0,0,0)
                col2.Add(time_box,0,0,0)

                def time_enable(evt):
                    self.time_ctrl1.Enable(False)
                    self.time_ctrl2.Enable(False)
                    self.torque_ctrl.Enable(False)
                    self.power_ctrl.Enable(False)

                    if   self.tsfd_radio is evt.GetEventObject():
                        self.time_ctrl1.Enable(True)
                    elif self.sr_radio is evt.GetEventObject():
                        self.time_ctrl2.Enable(True)
                    elif self.tfd_radio is evt.GetEventObject():
                        self.torque_ctrl.Enable(True)
                    elif self.pfd_radio is evt.GetEventObject():
                        self.power_ctrl.Enable(True)

                    
                self.Bind(wx.EVT_RADIOBUTTON, time_enable, self.tsfd_radio)
                self.Bind(wx.EVT_RADIOBUTTON, time_enable, self.sr_radio)
                self.Bind(wx.EVT_RADIOBUTTON, time_enable, self.tfd_radio)
                self.Bind(wx.EVT_RADIOBUTTON, time_enable, self.pfd_radio)


                
                ctrlsizer.Add(col1, 0,0,0)
                ctrlsizer.Add(col2, 0,0,0)
                sizer.Add(ctrlsizer, 1, wx.EXPAND|wx.ALL,10)

                # Ok/cancel controls
                hline = wx.StaticLine(self, -1, size=(20,-1),
                                      style=wx.LI_HORIZONTAL)
                sizer.Add(hline, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|
                          wx.RIGHT|wx.TOP, 0)
                
                box = wx.BoxSizer(wx.HORIZONTAL)
                box.Add(wx.Button(self, wx.ID_OK, "Import"), 0 ,
                        wx.ALIGN_CENTRE|wx.ALL, 5),
                box.Add(wx.Button(self, wx.ID_CANCEL, "Cancel"), 0 ,
                        wx.ALIGN_CENTRE|wx.ALL, 5),
                sizer.Add(box,0,0)

                self.SetSizer(sizer);sizer.Fit(self)
                self.SetAutoLayout(True)
                self.SetSize((300,300))

            def get_args(self):
                args = {}
                args['rpm_col'] = int(self.rpm.GetStringSelection())
                args['afr_col'] = int(self.afr.GetStringSelection())
                args['knock_col'] = int(self.knock.GetStringSelection())
                args['ts_col'] = int(self.ts.GetStringSelection())
                if self.tsfd_radio.GetValue():
                    args['time_col'] = \
                         int(self.time_ctrl1.GetStringSelection())
                elif self.sr_radio.GetValue():
                    args['sample_rate'] = self.time_ctrl2.GetValue()
                elif self.tfd_radio.GetValue():
                    args['torque_col'] = \
                         int(self.torque_ctrl.GetStringSelection())
                elif self.pfd_radio.GetValue():
                    args['power_col'] = \
                         int(self.power_ctrl.GetStringSelection())

                return args
            
        dlg = wx.FileDialog(self, "Choose a file", os.getcwd(), "",
                           DYNOFILETYPES, wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            data = dyno.read_csv(path)
            import_dlg = ImportDialog(self, -1, "import:" + path, data)
            if import_dlg.ShowModal() == wx.ID_OK:
                kwargs = import_dlg.get_args()

                r = dyno.DynoRun()
                r.Import(data,  **kwargs)
                self.AddRun(r)
    #__________________________________________________________________________
    def LoadDyno(self, e = None):
                        
        dlg = wx.FileDialog(self, "Choose a file", os.getcwd(), "",
                           DYNOFILETYPES, wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            r = dyno.DynoRun()
            try:
                r.Load(path)
            except IOError, mesg:
                FileError(self, str(mesg))
                self.LoadDyno()
                return
                
            self.AddRun(r)
    #__________________________________________________________________________
    def SaveDyno(self, e = None):
        if self.selected >= 0 and self.selected < len(self.runs):
            run = self.runs[self.selected]
        else:
            return False

        dlg = wx.FileDialog(self, "Save dyno #%d run as..." % self.selected,
                            os.getcwd(), "",
                            DYNOFILETYPES, wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            try:
                run.Save(path)
            except IOError, mesg:
                FileError(self, str(mesg))
    #__________________________________________________________________________
    def ViewDynoData(self, e = None):
        #_____________________________________________________________________
        class DynoData(wx.Frame):
            def __init__(self, parent, ID, run, title = None,
                         pos = wx.DefaultPosition,
                         size = wx.DefaultSize, style = wx.DEFAULT_FRAME_STYLE,
                         ):
                
                wx.Frame.__init__(self, parent, ID, title,
                                  pos, size, style)

                panel = wx.Panel(self, -1)
                self.panel = panel
                sizer = wx.BoxSizer(wx.HORIZONTAL)
            
                # Data list                
                list = parent.MyListCtrl(panel, -1, style=wx.LC_REPORT)
                self.list = list

                self.SetValues(run)
                # this keeps the list the panel size
                def OnPSize(e, win = panel):
                    panel.SetSize(e.GetSize())
                    list.SetSize(e.GetSize())
                    w,h = self.GetClientSizeTuple()
                    list.SetDimensions(0, 0, w, h)
                wx.EVT_SIZE(self, OnPSize)

                sizer.Add(list,0)
                panel.SetSizer(sizer);panel.SetAutoLayout(True);
                sizer.Fit(panel)
                self.SetSize((400,200))
                self.Show(True)

            def SetValues(self, run):
                self.list.ClearAll()
                self.list.InsertColumn(0, "RPM")
                self.list.InsertColumn(1, "Torque")
                self.list.InsertColumn(2, "Power")

                t = run.torque()
                h = run.hp()
                for i in range(0, len(t)):
                    self.list.InsertStringItem(i,str(t[i][0]))
                    self.list.SetStringItem(i, 1,str(t[i][1]))
                    self.list.SetStringItem(i, 2,str(h[i][1]))


        if self.selected >= 0 and self.selected < len(self.runs):
            run = self.runs[self.selected]
        else:
            return False

        d = DynoData(self, -1, run, title = "Dyno Run #%d" % self.selected)
        self.viewing[self.selected] = d

    #__________________________________________________________________________
    def get_selected(self):
        if self.selected >= 0 and self.selected < len(self.runs):
            run = self.runs[self.selected]
        else:
            run = False
        return run
    #__________________________________________________________________________
    def gnuplot_manual(self, evt = None):
        dlg = self.GnuplotDialog(self, -1)
        if dlg.ShowModal() == wx.ID_OK:
            data = []
            label= []
            for i in dlg.selected:
                data.append(self.runs[i].torque())
                data.append(self.runs[i].hp())
                label.append("Torque %d" % i)
                label.append("Power %d" % i)
            if len(data) > 0:
                gnuplot.plot(data, terminal = arch.GNUPLOT_TERMINAL,
                             output = arch.GNUPLOT_OUTPUT, labels = label)
    #__________________________________________________________________________
    def plot_seperate(self, evt = None):
        """Plot to a new frame"""

        run = self.get_selected()
        if run:
            frame = wx.Frame(self, -1, "Run #%d" % self.selected)
            frame.Show(True)
            p = rpmplot.PlottingPanel(frame, -1)
            p.Update(run)

    #__________________________________________________________________________
    def plot_run(self, evt = None):
        run = self.get_selected()
        if run:
            self.plot.Update(run)

    #__________________________________________________________________________
    def trim_threshold(self, evt = None):
        class trimdlg(wx.Dialog):
            def __init__(self, parent, id, title):
                pre = wx.PreDialog()
                pre.Create(parent, id, title)
                self.this = pre.this

                sizer = wx.BoxSizer(wx.VERTICAL)
                self.input = IntCtrl(self,-1)
                self.input.SetValue(0)
                sizer.Add(self.input, 0, wx.ALL, 5)
                
                box = wx.BoxSizer(wx.HORIZONTAL)
                
                box.Add(wx.Button(self, wx.ID_OK), 0 ,
                        wx.ALIGN_CENTRE|wx.ALL, 5),
                box.Add(wx.Button(self, wx.ID_CANCEL), 0 ,
                        wx.ALIGN_CENTRE|wx.ALL, 5),
                sizer.AddSizer(box, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
                self.SetSizer(sizer)
                sizer.Fit(self)
                self.SetAutoLayout(True)
            
        run = self.get_selected()
        if run:
            dlg = trimdlg(self, -1, "Trim above..")
            if dlg.ShowModal() == wx.ID_OK:
                thr = dlg.input.GetValue()
                run.trim(threshold=thr)
                self.UpdateListAndPlot(self.selected)

    #__________________________________________________________________________
    def trim(self, n):
        run = self.get_selected()
        if run:
            run.trim(size=n)
            self.UpdateListAndPlot(self.selected)

    #__________________________________________________________________________
    def SmoothSavGol(self, run):
        if self.selected >= 0 and self.selected < len(self.runs):
            run = self.runs[self.selected]
        else:
            return False
        run.Smooth(smooth.SavGol)

        self.UpdateListAndPlot(self.selected)
#        try:
#            dd = self.viewing[self.selected]
#        except KeyError:
#            pass
    #__________________________________________________________________________
    def SmoothBox(self, run):
        run = self.get_selected()
        if run:
            run.Smooth(smooth.box)

        self.UpdateListAndPlot(self.selected)
#        try:
#            dd = self.viewing[self.selected]
#        except KeyError:
#            pass
    #__________________________________________________________________________
    def SmoothNNA(self, w):
        run = self.get_selected()
        if run:
            run.Smooth(smooth.NNA, {"window": w})
        self.UpdateListAndPlot(self.selected)
    #__________________________________________________________________________
    def SmoothRA(self, run):
        run = self.get_selected()
        if run:
            run.Smooth(smooth.RunningAverage)
            self.UpdateListAndPlot(self.selected)
    #__________________________________________________________________________
    def UpdateListAndPlot(self,nrun):
        run = self.runs[nrun]

        t = run.torque()
        mt = t[0]
        for cur in t:
            if cur[1] > mt[1]:
                mt = cur
        mt_str = "%.2f" % mt[1] + "@" + "%d" % mt[0]
        self.list.SetStringItem(nrun, 1, str(mt_str))

        ta = run.torque_area()
        tas= "%.2f" % ta
        self.list.SetStringItem(nrun, 2, tas)

        p = run.hp()
        mp = p[0]
        for cur in p:
            if cur[1] > mp[1]:
                mp = cur
        mp_str = "%.2f" % mp[1] + "@" + "%d" % mp[0]
        self.list.SetStringItem(nrun, 3, str(mp_str))

        hpa = run.hp_area()
        hpas= "%.2f" % hpa
        self.list.SetStringItem(nrun, 4, hpas)        

        afr = run.afr()
        ma = afr[0]
        for cur in afr:
            if cur[1] > ma[1]:
                ma = cur
        ma_str = "%.2f" % ma[1] + "@" + "%d" % ma[0]
        self.list.SetStringItem(nrun, 5, ma_str)        

        self.plot_run()
        
    #__________________________________________________________________________
    def AddRun(self, run):
        self.runs.append(run)
        items = self.list.GetItemCount()
        s = "Run #%d" % items
        self.list.InsertStringItem(items, s)
        self.UpdateListAndPlot(items)
        self.mainmenu.Enable(203, 1)
        self.mainmenu.Enable(300, 1)
        self.mainmenu.Enable(302, 1)
            
if __name__ == "__main__":
    class testApp(wx.App):
        def OnInit(self):
            tID = wx.NewId()
            
            self.frame = DynoList(None, "DynoRunList")
            self.SetTopWindow(self.frame)
            self.frame.Show(True)
            return True

    app = testApp(0)
    app.MainLoop()
    
