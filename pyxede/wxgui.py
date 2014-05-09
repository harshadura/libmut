#!/usr/bin/pythonw 
############################################################################
#
# wxgui.py
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
# wxWindows GUI for pyXede. 
#
############################################################################
import string

__version__ = string.split('$Revision: 1.13 $')[1]
__date__ = string.join(string.split('$Date: 2006/02/10 00:50:02 $')[1:3], ' ')
__author__ = ('C. Donour Sizemore <donour@cs.uchicago.edu>',)

RELEASE_VERSION = "1.5"

import threading
import time
import os
from Queue import Queue

import arch

if arch.WXVERSION:
    import wxversion
    wxversion.select("2.6")
    

import pyxede
import dyno
from io_array import IO_ARRAY
import wxdyno

import wx
import wx.py
from wxPython.lib.mixins.listctrl import wxListCtrlAutoWidthMixin
from wxPython.lib.filebrowsebutton import FileBrowseButton
from wxPython.lib.dialogs import wxScrolledMessageDialog 
from wxPython.lib import newevent

debugfile = open("wx_debug","w")
def debug(str):
    debugfile.write(str+"\n")
    debugfile.flush()

ID_ABOUT     = 101
ID_LOG       = 102
ID_HSLOG     = 103
ID_EXIT      = 110
ID_CONFIG    = 500
ID_CLEAR     = 501
ID_CONNECT   = 503
ID_DISCONN   = 504
ID_VIEW_DYNO = 505
ID_VIEW_MCP  = 506
ID_DYNO      = 601

ID_ABOUT  = 701

LOGFILETYPES  = "Pyxede Logs (*.csv)|*.csv|" \
                "All Files|*.*"

MARK_MESG = "marked!"

# Custom events for updating GUI from worker threads
UpdateDynoEvent, EVT_UPDATE_DYNO    = newevent.NewEvent()
UpdateMonEvent,  EVT_UPDATE_MON     = newevent.NewEvent()
UpdateLogEvent,  EVT_UPDATE_LOG     = newevent.NewEvent()
UpdateHSLogEvent,  EVT_UPDATE_HSLOG = newevent.NewEvent()

GUI_REFRESH_TIME  = 0.5  # in seconds
SAMPLERATE_UPDATE = 0.5  
YIELD_SLEEP_TIME  = 0.001


def FileError(parent, mesg):
    error_dlg = wx.MessageDialog(parent,mesg,"File Error",
                                wx.OK | wx.ICON_INFORMATION)
    error_dlg.ShowModal()


def build_sensor_select(dlg,sizer, title):
    label = pyxede.INPUT_NAMES

    box = wx.StaticBox(dlg, -1, title)
    controls = wx.StaticBoxSizer(box,wx.HORIZONTAL)
    
    col1 = wx.BoxSizer(wx.VERTICAL)
    
    sID = wx.NewId()
    dlg.rpm = wx.CheckBox(dlg,   sID  , "RPM")
    dlg.rpm.SetValue(True);dlg.rpm.Disable()
    col1.Add(dlg.rpm, 0,0)
    dlg.cas = wx.CheckBox(dlg,   sID+1, "CAS")
    col1.Add(dlg.cas, 0 , 0)
    dlg.amapi = wx.CheckBox(dlg, sID+2,  label['AN0'])
    col1.Add(dlg.amapi, 0 , 0)
    dlg.amapo = wx.CheckBox(dlg, sID+3, "Analog MAP Out")
    col1.Add(dlg.amapo, 0 , 0)
    dlg.amafi = wx.CheckBox(dlg, sID+4,  label["AN1"])
    col1.Add(dlg.amafi, 0 , 0)
    dlg.amafo = wx.CheckBox(dlg, sID+5, "Analog MAF Out")
    col1.Add(dlg.amafo, 0 , 0)
    
    col2 = wx.BoxSizer(wx.VERTICAL)
    dlg.knock = wx.CheckBox(dlg, sID+6,  "Knock Attenuate")
    col2.Add(dlg.knock, 0 , 0)
    dlg.bodc = wx.CheckBox(dlg,  sID+8,  "Boost Output DC")
    col2.Add(dlg.bodc, 0 , 0)
    dlg.fmafi = wx.CheckBox(dlg, sID+9,  "Freq MAF In")
    col2.Add(dlg.fmafi, 0 , 0)
    dlg.fmafo = wx.CheckBox(dlg, sID+10, "Freq MAF Out")
    col2.Add(dlg.fmafo, 0 , 0)
    dlg.tpsi = wx.CheckBox(dlg,  sID+11, "Analog TPS In")
    col2.Add(dlg.tpsi, 0 , 0)
    dlg.tpso = wx.CheckBox(dlg,  sID+12, "Analog TPS Out")
    col2.Add(dlg.tpso, 0 , 0)
    
    controls.Add(col1, 0,0)
    controls.Add(col2, 0,0)

    bsizer = wx.BoxSizer()
    bsizer.Add(controls,0,0)
    sizer.Add(bsizer, 1,wx.EXPAND | wx.ALL, 5)

def dialog_to_sources(dlg):
    # build log line
    sources  = 0
    label = "# Time"
    
    if dlg.rpm.GetValue():
        label = label + ",RPM"
        sources = sources | pyxede.LOG_RPM

    if dlg.cas.GetValue():
        label = label + ",CAS"
        sources = sources | pyxede.LOG_TIMING_OUT

    if dlg.amapi.GetValue():
        label = label + "," + pyxede.INPUT_NAMES['AN0']
        sources = sources | pyxede.LOG_ANALOG_MAP_IN
    if dlg.amapo.GetValue():
        label = label + ",AnalogMAPOut"
        sources = sources | pyxede.LOG_ANALOG_MAP_OUT
                
    if dlg.amafi.GetValue():
        label = label + ", " + pyxede.INPUT_NAMES['AN1']
        sources = sources | pyxede.LOG_ANALOG_MAF_IN
    if dlg.amafo.GetValue():
        label = label + ",AnalogMAFOut"
        sources = sources | pyxede.LOG_ANALOG_MAF_OUT

    if dlg.bodc.GetValue():
        label = label + ",BoostODC"
        sources = sources | pyxede.LOG_WGSOL_OUT
                
    if dlg.fmafi.GetValue():
        label = label + ",FreqMAFIn"
        sources = sources | pyxede.LOG_FREQ_MAF_IN
    if dlg.fmafo.GetValue():
        label = label + ",FreqMAFOut"
        sources = sources | pyxede.LOG_FREQ_MAF_OUT

    if dlg.tpsi.GetValue():
        label = label + ",AnalogTPSIn"
        sources = sources | pyxede.LOG_TPS_IN
    if dlg.tpso.GetValue():
        label = label + ",AnalogTPSOut"
        sources = sources | pyxede.LOG_TPS_OUT
                 
    return sources, label


class MyApp(wx.App):
    #__________________________________________________________________________
    class MyListCtrl(wx.ListCtrl, wxListCtrlAutoWidthMixin):
        def __init__(self, parent, id, pos = wx.DefaultPosition,
                     size = wx.DefaultSize, style = 0):
            wx.ListCtrl.__init__(self,parent,id,pos,size,style)
            wxListCtrlAutoWidthMixin.__init__(self)    
    
    #__________________________________________________________________________
    class XedeProducer:
        def __init__(self, frame):
            self.done = Queue(1)
            self.active = threading.Lock()

            self.frame  = frame
            self.paused = Queue(1)
            self.marked = Queue()
        #______________________________________________________________________
        def stop(self):
            if not self.paused.empty():
                self.unpause()
            self.done.put(1)
            self.active.acquire()
            self.active.release()
        #______________________________________________________________________
        def monitor(self, port):
            if self.active.acquire(0):
                threading.Thread(None, self.monitor_internal, None,
                                 (port,)).start()
                return True
            else:
                return False
            
        def monitor_internal(self, port):
            while self.done.empty():
                sleep = arch.time_func()
                
                rpm   = port.RPM()
                afr   = port.AFR()
                cas   = port.CAS()
                sk    = port.SMARTKnock()
                bodc  = port.BoostODC()
                fmafi = port.FreqMAFIn()
                fmafo = port.FreqMAFOut()

                m = port.CurrentMap()
                e = UpdateMonEvent(
                    RPM    = str(rpm  ),
                    AFR    = str(afr  ),
                    CAS    = str(cas  ),
                    SK     = str(sk   ),
                    bodc   = str(bodc ),
                    fmafi  = str(fmafi),
                    fmafo  = str(fmafo),
                    cur_map= str(m    )
                    )
                while arch.time_func() - sleep < GUI_REFRESH_TIME:
                    time.sleep(YIELD_SLEEP_TIME)

                wx.PostEvent(self.frame,e)

            self.done.get()
            self.active.release()
        #______________________________________________________________________
        def pause(self):
            self.paused.put(1)
        def unpause(self):
            self.paused.get()
        def mark(self):
            if self.paused.empty():
                self.marked.put(MARK_MESG)
            
        def log(self, outfile, funcs, parent):
            if self.active.acquire(0):
                threading.Thread(None, self.log_internal, None,
                                 (outfile, funcs, parent)).start()
                return True
            else:
                return False            
            
        def log_internal(self, outfile,funcs, parent):
            start_time = arch.time_func()
            sr_update = 0.0
            while self.done.empty():
                t = arch.time_func() - start_time
                if not self.marked.empty():
                    m = self.marked.get()
                    print >>outfile,  t, m

                sr_start = arch.time_func()
                
                if self.paused.empty():
                    line = str(t)
                    for f in funcs:
                        value = f()
                        line = line + "," + str(value)
                    if self.done.empty():
                        print >>outfile, line

                else:
                    # tricky way to "stop" when paused
                    self.paused.put(1)
                    self.paused.get(1)
                    
                if t - sr_update > SAMPLERATE_UPDATE:
                    sr_update = t
                    sr = arch.time_func() - sr_start
                    sample_rate = 1.0 / sr
                    e = UpdateLogEvent(rate = str(int(sample_rate)))
                    wx.PostEvent(parent,e)               

            self.done.get()
            self.active.release()
    #__________________________________________________________________________
    class AboutBox(wx.Dialog):
        def __init__(self, parent):
            pre = wx.PreDialog()
            pre.Create(parent, -1, "About pyXede v%s" % RELEASE_VERSION)
            self.this = pre.this 

            sizer = wx.BoxSizer(wx.VERTICAL)

            hsizer= wx.BoxSizer(wx.HORIZONTAL)
            txt = wx.StaticText(self, -1, "wx.gui version: ")
            hsizer.Add(txt, 1,wx.WEST, 10)
            txt = wx.StaticText(self, -1, __version__)
            hsizer.Add(txt, 0,0)
            sizer.Add(hsizer,0,0)

            hsizer= wx.BoxSizer(wx.HORIZONTAL)
            txt = wx.StaticText(self, -1, "pyxede version: ")
            hsizer.Add(txt, 1,wx.WEST, 10)
            txt = wx.StaticText(self, -1, pyxede.__version__)
            hsizer.Add(txt, 0,0)
            sizer.Add(hsizer,0,0)

            hsizer= wx.BoxSizer(wx.HORIZONTAL)
            txt = wx.StaticText(self, -1, "dyno.py version: ")
            hsizer.Add(txt, 1,wx.WEST, 10)
            txt = wx.StaticText(self, -1, dyno.__version__)
            hsizer.Add(txt, 0,0)
            sizer.Add(hsizer,0,0)

            hsizer= wx.BoxSizer(wx.HORIZONTAL)
            txt = wx.StaticText(self, -1, "gnuplot.py version: ")
            hsizer.Add(txt, 1,wx.WEST, 10)
            txt = wx.StaticText(self, -1, dyno.gnuplot.__version__)
            hsizer.Add(txt, 0,0)
            sizer.Add(hsizer,0,0)

            hsizer= wx.BoxSizer(wx.HORIZONTAL)
            txt = wx.StaticText(self, -1, "rpmplot.py version: ")
            hsizer.Add(txt, 1,wx.WEST, 10)
            txt = wx.StaticText(self, -1, wxdyno.rpmplot.__version__)
            hsizer.Add(txt, 0,0)
            sizer.Add(hsizer,0,0)
            
            txt = wx.StaticText(self, -1, "Authors:")
            sizer.Add(txt,1,wx.WEST, 10)
            for a in __author__:
                txt = wx.StaticText(self, -1, a)
                sizer.Add(txt,1,wx.WEST, 15)

            # a line
            hline = wx.StaticLine(self, -1, size=(20,-1),
                                style=wx.LI_HORIZONTAL)
            sizer.Add(hline, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|
                      wx.RIGHT|wx.TOP, 5)

            txt = wx.StaticText(self, -1,
                               "pyXede is copyright the authors 2004-6")
            sizer.Add(txt,1, wx.EAST | wx.WEST, 10)

            # Controls
            ctrls = wx.BoxSizer(wx.HORIZONTAL)
            btn = wx.Button(self, wx.ID_OK, "Ok")
            ctrls.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            bID = wx.NewId()
            btn = wx.Button(self, bID, "License")
            ctrls.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            def show_license(event):
                f = open("COPYING")
                m = f.read()
                dlg = wxScrolledMessageDialog(self, m , "pyXede License",
                                              size=(640,400))
                dlg.ShowModal()
            wx.EVT_BUTTON(self, bID, show_license)
            sizer.Add(ctrls,0,wx.ALIGN_CENTRE)
            self.SetSizer(sizer);self.SetAutoLayout(True); sizer.Fit(self)
    
    def ShowAbout(self, e = None):
        about = self.AboutBox(self.frame)
        about.ShowModal()

    #__________________________________________________________________________
    def OnInit(self):
        self.port    = None
        
        tID = wx.NewId()
                
        frame = wx.Frame(None, -1, "pyXede")
        self.frame=frame
        self.prod = self.XedeProducer(frame)

        panel = wx.Panel(self.frame, -1)
        frame.CreateStatusBar()
        frame.SetStatusText("No Xede Connected")

        sizer    = wx.BoxSizer(wx.VERTICAL)

        self.data_display = self.MyListCtrl(panel, tID, pos=wx.Point(0, 0),
                                       size = (335,100),
                                       style =
                                       wx.LC_REPORT     |
                                       wx.LC_HRULES     |
                                       wx.LC_SINGLE_SEL )
        sizer.Add(self.data_display, 0,wx.ALL, 5)
        
        self.data_display.InsertColumn(0, "Engine State", width=250)
        self.data_display.InsertColumn(1, "Value")
        self.data_display.InsertStringItem(0, "")
        self.data_display.SetStringItem(   0,0, "RPM         ")
        self.data_display.InsertStringItem(1, "")
        self.data_display.SetStringItem(   1,0, "Timing")
        self.data_display.InsertStringItem(2, "")
        self.data_display.SetStringItem(   2,0, "A/F Ratio   ")
        self.data_display.InsertStringItem(3, "")
        self.data_display.SetStringItem(   3,0, "SMART Knock ")

        self.data_display.InsertStringItem(4, "")        
        self.data_display.SetStringItem(   4,0, "Boost Ouput ")
        self.data_display.InsertStringItem(5, "")
        self.data_display.SetStringItem(   5,0, "Freq MAF In ")
        self.data_display.InsertStringItem(6, "")
        self.data_display.SetStringItem(   6,0, "Freq MAF Out")


        def OnMonUpdate(evt):
            self.data_display.SetStringItem(0,1, evt.RPM  )
            self.data_display.SetStringItem(1,1, evt.CAS  )
            self.data_display.SetStringItem(2,1, evt.AFR  )
            self.data_display.SetStringItem(3,1, evt.SK   )
            self.data_display.SetStringItem(4,1, evt.bodc )
            self.data_display.SetStringItem(5,1, evt.fmafi)
            self.data_display.SetStringItem(6,1, evt.fmafo)
            self.frame.SetStatusText("Xede Connected, Current Bank: " + \
                                      evt.cur_map)
            
        EVT_UPDATE_MON(self, OnMonUpdate)

        def OnPSize(e, win = panel):
            panel.SetSize(e.GetSize())
            w,h = panel.GetClientSizeTuple()
            self.data_display.SetSize(e.GetSize())
            self.data_display.SetDimensions(0, 0, w, h)
        wx.EVT_SIZE(panel, OnPSize)

        # Setting up the menu.
        filemenu= wx.Menu()
        filemenu.Append(ID_LOG , "Log Data to file"," Log engine data to file")
        filemenu.Append(ID_HSLOG , "High Speed Data Log"," ")
        filemenu.AppendSeparator()
        filemenu.Append(ID_DYNO, "Perform Road Dyno",
                        " Perform Road Dyno measurement")
        filemenu.AppendSeparator()
        filemenu.Append(ID_CONFIG,"Configure"," Configure Xede")
        filemenu.AppendSeparator()
        filemenu.Append(ID_EXIT, "E&xit"," Terminate the program")

        portmenu = wx.Menu()
        portmenu.Append(ID_CONNECT,"Connect\tCtrl+c", "Connect reset device")
        portmenu.Append(ID_DISCONN,"Disconnect\tCtrl+d", "Close connection")

        viewmenu = wx.Menu()
        viewmenu.Append(ID_VIEW_DYNO,"Dyno Runs", "")
        viewmenu.Append(ID_VIEW_MCP ,"Master Control Program", "")

        helpmenu = wx.Menu()
        helpmenu.Append(ID_ABOUT,"About"," About pyXede")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        self.menubar = menuBar
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        menuBar.Append(portmenu,"&Port")
        menuBar.Append(viewmenu,"View")
        menuBar.Append(helpmenu,"&Help")


        #FIXME these should be turned off
        menuBar.Enable(ID_LOG   , 0)
        menuBar.Enable(ID_HSLOG , 0)
        menuBar.Enable(ID_DYNO  , 0)
        
        frame.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        wx.EVT_MENU(frame, ID_EXIT    , self.OnQuit)
        wx.EVT_MENU(frame, ID_HSLOG   , self.HighSpeedLogSetup)
        wx.EVT_MENU(frame, ID_LOG     , self.LogSetup)
        wx.EVT_MENU(frame, ID_CONFIG  , self.Configure)
        wx.EVT_MENU(frame, ID_CONNECT , self.OpenPort)
        wx.EVT_MENU(frame, ID_DISCONN , self.ClosePort)
        wx.EVT_MENU(frame, ID_DYNO    , self.RoadDynoDlg)
        wx.EVT_MENU(frame, ID_VIEW_DYNO,self.ViewDyno)
        wx.EVT_MENU(frame, ID_VIEW_MCP,self.ViewMCP)


        wx.EVT_MENU(frame, ID_ABOUT   , self.ShowAbout)
  
        self.SetTopWindow(frame)

        panel.SetSizer(sizer)
        frame.Show(True)
        frame.SetSize((332,250))

        self.dynolist=wxdyno.DynoList(self.frame, "pyXede :: Dyno Runs")

        return True

    #__________________________________________________________________________
    def ViewDyno(self, evt = None):
        self.dynolist.Show(True)
    #__________________________________________________________________________
    def ViewMCP(self, evt = None):
        frame = wx.Frame(self.frame, -1, "MCP")
        wx.py.crust.Crust(frame, intro = \
                       '\"With the information I can access, I can run things'\
                       ' 900 to 1200 times better than any human.\" ')
        frame.Show(True)
    #__________________________________________________________________________
    def LogFile(self, filename, label, funcs):
        #______________________________________________________________________
        class LogDialog(wx.Dialog):

            def mark(self, e = None):
                self.prod.mark()
                
            def pause(self, e = None):
                if self.paused:
                    self.pause_btn.SetLabel("Pause")
                    self.prod.unpause()
                    self.paused = False
                else:
                    self.pause_btn.SetLabel("Unpause")
                    self.prod.pause()
                    self.paused = True
                
            def __init__(self, parent, ID, title, outfile, prod, funcs,
                         pos = wx.DefaultPosition,
                     size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE):
                pre = wx.PreDialog()
                pre.Create(parent, ID, title, pos, size, style)
                self.this = pre.this
                
                sizer = wx.BoxSizer(wx.VERTICAL)

                box  = wx.BoxSizer(wx.HORIZONTAL)
                txt = wx.StaticText(self, -1, "Sample Rate: ")
                box.Add(txt, 1, wx.ALL, 4)
                self.samplerate = wx.StaticText(self, -1, "0  ")
                box.Add(self.samplerate, 1, wx.ALL, 4)
                sizer.Add(box, 0, wx.EXPAND|wx.EAST|wx.WEST);

                def OnLogUpdate(evt):
                    self.samplerate.SetLabel(evt.rate)

                EVT_UPDATE_LOG(self, OnLogUpdate)
 
                # a line
                hline = wx.StaticLine(self, -1, size=(20,-1),
                                     style=wx.LI_HORIZONTAL)
                sizer.Add(hline, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|
                          wx.RIGHT|wx.TOP, 5)

                # Controls

                bID = wx.NewId()
                box = wx.BoxSizer(wx.HORIZONTAL)

                btn = wx.Button(self, bID, "Mark Event")
                box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                self.pause_btn = wx.Button(self, bID+1, "Pause")
                box.Add(self.pause_btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

                wx.EVT_BUTTON(self, bID,   self.mark)
                wx.EVT_BUTTON(self, bID+1, self.pause)

                box.Add(wx.Button(self, wx.ID_CANCEL, "Stop"), 0 ,
                        wx.ALIGN_CENTRE|wx.ALL, 5),
                sizer.AddSizer(box, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
                
                self.SetSizer(sizer);self.SetAutoLayout(True); sizer.Fit(self)

                self.paused = False
                self.prod  = prod
                # failure means logging isn't happening
                if not prod.log(outfile,funcs, self):
                    raise "Failed to acquire logging lock"
                    
        #______________________________________________________________________


        f = open(filename, "w")
        print >>f, label
        self.prod.stop()

        diag = LogDialog(self.frame, 0, "Logging to '%s'" % filename,
                         f, self.prod, funcs)
        
        diag.ShowModal()
        self.prod.stop()
        self.StartEngineMonitor()

    #__________________________________________________________________________
    def LogSetup(self, e = None):
        class LogQueryDialog(wx.Dialog):
            #__________________________________________________________________
            def QuerySaveFile(self, e = None):
                filetypes = "Comma Delimited Logs (*.csv)|*.csv|" \
                            "All files (*.*)|*.*"
                
                file_dlg = wx.FileDialog(self, "Save log as...",
                                        os.getcwd(), "", filetypes, wx.SAVE)
                if file_dlg.ShowModal() == wx.ID_OK:
                    path = file_dlg.GetPath()
                    debug( path)
                    self.filename.SetValue(path)
                    return path
                return None
            #__________________________________________________________________
            def __init__(self, parent, ID, title, pos = wx.DefaultPosition,
                     size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE):
                pre = wx.PreDialog()
                pre.Create(parent, ID, title, pos, size, style)
                self.this = pre.this
                sizer = wx.BoxSizer(wx.VERTICAL)

                build_sensor_select(self,sizer,"Available Inputs")

                controls2 = wx.BoxSizer(wx.HORIZONTAL)
                # FIXME: this should be FileBrowse widget
                self.filename = wx.TextCtrl(self, -1, os.getcwd(),
                                           size=(300, -1))
                controls2.Add(self.filename, 0, wx.EAST|wx.WEST|wx.EXPAND, 5)

                sizer.Add(controls2, 0, 0)
                
                hline = wx.StaticLine(self, -1, size=(20,-1),
                                     style=wx.LI_HORIZONTAL)
                sizer.Add(hline, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|
                          wx.RIGHT|wx.TOP, 5)
                
                box = wx.BoxSizer(wx.HORIZONTAL)
                btn = wx.Button(self, wx.ID_OK, " Log ")
                btn.SetDefault()
                box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                
                btn = wx.Button(self, wx.ID_CANCEL, " Cancel ")
                box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                bID = wx.NewId()
                box.Add(wx.Button(self, bID, "Browse"), 0,
                        wx.ALIGN_CENTRE|wx.ALL, 5),

                wx.EVT_BUTTON(self, bID, self.QuerySaveFile)
                
                sizer.AddSizer(box, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
                self.SetSizer(sizer);self.SetAutoLayout(True); sizer.Fit(self)
        #______________________________________________________________________
       
        diag = LogQueryDialog(self.frame, 0, "Datalog to File")
        if diag.ShowModal() == wx.ID_OK:
            f = diag.filename.GetValue()

            # build log line
            label = "# Time,"
            func  = []
            if diag.rpm.GetValue():
                label = label + "RPM,"
                func.append(self.port.RPM)
            if diag.cas.GetValue():
                label = label + "CAS,"
                func.append(self.port.CAS)

            if diag.amapi.GetValue():
                label = label + "%s," % pyxede.INPUT_NAMES['AN0']
                func.append(self.port.AnalogMAPIn)
            if diag.amapo.GetValue():
                label = label + "AnalogMAPOut,"
                func.append(self.port.AnalogMAPOut)

            if diag.amafi.GetValue():
                label = label + "%s," % pyxede.INPUT_NAMES['AN1']
                func.append(self.port.AnalogMAFIn)
            if diag.amafo.GetValue():
                label = label + "AnalogMAFOut,"
                func.append(self.port.AnalogMAFOut)

            if diag.knock.GetValue():
                label = label + "Knock,"
                func.append(self.port.Knock)

            if diag.bidc.GetValue():
                label = label + "BoostIDC,"
                func.append(self.port.BoostIDC)
            if diag.bodc.GetValue():
                label = label + "BoostODC,"
                func.append(self.port.BoostODC)

            if diag.fmafi.GetValue():
                label = label + "FreqMAFIn,"
                func.append(self.port.FreqMAFIn)
            if diag.fmafo.GetValue():
                label = label + "FreqMAFOut,"
                func.append(self.port.FreqMAFOut)

            if diag.fmafi.GetValue():
                label = label + "AnalogTPSIn,"
                func.append(self.port.AnalogTPSOut)
            if diag.fmafo.GetValue():
                label = label + "AnalogTPSOut,"
                func.append(self.port.AnalogTPSOut)

            
            try:
                self.LogFile(f, label, func)
            except IOError, mesg:
                FileError(self.frame, str(mesg))
    #__________________________________________________________________________
    def HighSpeedLogFile(self, filehandle, srcs):
        #______________________________________________________________________
        class LogDialog(wx.Dialog):
                
            def __init__(self, parent, ID, title, destfile,
                         pos = wx.DefaultPosition,
                         size = wx.DefaultSize,style =wx.DEFAULT_DIALOG_STYLE):
                pre = wx.PreDialog()
                pre.Create(parent, ID,title, pos, size, style)
                self.this = pre.this
                sizer = wx.BoxSizer(wx.VERTICAL)

                box = wx.StaticBox(self, -1)
                bsizer = wx.StaticBoxSizer(box,wx.VERTICAL)

                line  = wx.BoxSizer(wx.HORIZONTAL)
                txt = wx.StaticText(self, -1, "Logging to: ")
                line.Add(txt, 0,0)
                txt = wx.StaticText(self, -1, destfile)
                line.Add(txt, 0,0)
                bsizer.Add(line, 0,0)

                self.sample_rate_value = 0
                line  = wx.BoxSizer(wx.HORIZONTAL)
                txt = wx.StaticText(self, -1, "Samplerate: ")
                line.Add(txt, 0,0)
                self.sample_rate = wx.StaticText(self, -1, "000 hz")
                line.Add(self.sample_rate, 0,0)
                bsizer.Add(line, 0,0)

                line  = wx.BoxSizer(wx.HORIZONTAL)
                txt = wx.StaticText(self, -1, "Duration: ")
                line.Add(txt, 0,0)
                self.duration = wx.StaticText(self, -1, "00:00:00.00")
                line.Add(self.duration, 0,0)                
                bsizer.Add(line, 0,0)

                sizer.Add(bsizer, 1,wx.EXPAND | wx.ALL, 5)

                # Controls
                bID = wx.NewId()
                box = wx.BoxSizer(wx.HORIZONTAL)

                box.Add(wx.Button(self, wx.ID_CANCEL, "Stop"), 0 ,
                        wx.ALIGN_CENTRE|wx.ALL, 5),
                sizer.AddSizer(box, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
                
                self.SetSizer(sizer);self.SetAutoLayout(True); sizer.Fit(self)
                #______________________________________________________________
                def OnHSLogUpdate(evt):
                    self.duration.SetLabel(evt.dur)
                    self.sample_rate.SetLabel(evt.sr)
                EVT_UPDATE_HSLOG(self, OnHSLogUpdate)

            def set_sample_rate(self,sr):
                self.sample_rate_value = sr                    
        #______________________________________________________________________
        def update_dialog(diag, finished = lambda : True):
            start = time.time()
            while not finished():
                elapsed = time.time() - start
                dur = int(elapsed)                # hours      min     seconds   
                duration = "%.2d:%.2d:%2.2f" % ( dur / 3600, dur / 60, elapsed - dur + dur % 60)
                sample_rate = "%.3d hz" % diag.sample_rate_value
                e = UpdateHSLogEvent(dur = duration, sr = sample_rate)
                wx.PostEvent(diag,e)               
                time.sleep(0.05)
        #______________________________________________________________________
        
        self.prod.stop()

        log_evt = threading.Event()
        diag = LogDialog(self.frame, 0, "Logging to " + filehandle.name,
                         filehandle.name)
        diag.duration.SetLabel("1:2:3:4")

        update = threading.Thread(None, update_dialog, None,
                             (diag, ),
                             { "finished" : log_evt.isSet} )

        t = threading.Thread(None, self.port.HighSpeedLog, None,
                             (srcs, filehandle),
                             { "finished" : log_evt.isSet,
                               "sample_rate": diag.set_sample_rate} )

        t.start()
        update.start()


        diag.ShowModal()

        log_evt.set()
        update.join()
        t.join()

        self.StartEngineMonitor()

    #__________________________________________________________________________
    def HighSpeedLogSetup(self, e = None):
        class LogQueryDialog(wx.Dialog):
            #__________________________________________________________________
            def __init__(self, parent, ID, title, pos = wx.DefaultPosition,
                     size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE):
                pre = wx.PreDialog()
                pre.Create(parent, ID, title, pos, size, style)
                self.this = pre.this
                sizer = wx.BoxSizer(wx.VERTICAL)

                build_sensor_select(self,sizer, "Available Inputs")

                controls2 = wx.BoxSizer(wx.HORIZONTAL)
                self.fbbc = FileBrowseButton(self, -1, size = (400,40),
                                             fileMask = LOGFILETYPES)
                self.fbbc.SetLabel("file:")
                controls2.Add(self.fbbc, 0,  wx.EAST | wx.WEST | wx.EXPAND, 0)

                sizer.Add(controls2, 0, 0)
                
                hline = wx.StaticLine(self, -1, size=(20,-1),
                                     style=wx.LI_HORIZONTAL)
                sizer.Add(hline, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|
                          wx.RIGHT|wx.TOP, 5)
                
                box = wx.BoxSizer(wx.HORIZONTAL)
                btn = wx.Button(self, wx.ID_OK, " Log ")
                btn.SetDefault()
                box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                
                btn = wx.Button(self, wx.ID_CANCEL, " Cancel ")
                box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                bID = wx.NewId()
                
                sizer.AddSizer(box, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
                self.SetSizer(sizer);self.SetAutoLayout(True); sizer.Fit(self)
        #______________________________________________________________________
       
        diag = LogQueryDialog(self.frame, 0, "High Speed Datalog to File")
        if diag.ShowModal() == wx.ID_OK:
            filename = diag.fbbc.GetValue()
            try:
                f = file(filename, "w")
            except IOError, mesg:
                FileError(self.frame, str(mesg))

            sources, label = dialog_to_sources(diag)

            self.HighSpeedLogFile(f, sources)
    #__________________________________________________________________________
    
    def StartEngineMonitor(self):
        if self.prod.monitor(self.port):
            self.menubar.Enable(ID_CONNECT,0)
            self.menubar.Enable(ID_CONFIG, 0)

            self.menubar.Enable(ID_LOG   , 1)
            self.menubar.Enable(ID_HSLOG , 1)
            self.menubar.Enable(ID_DYNO  , 1)
        
    #__________________________________________________________________________
    def OpenPort(self,e = None):
        class OpenFailDialog(wx.Dialog):
            def __init__(self, parent, ID, title, pos = wx.DefaultPosition,
                         size = wx.DefaultSize, style =wx.DEFAULT_DIALOG_STYLE,
                         mesg = ""):
                
                pre = wx.PreDialog()
                pre.Create(parent, ID, title, pos, size, style)
                self.this = pre.this
                sizer = wx.BoxSizer(wx.VERTICAL)

                label = wx.StaticText(self, -1, mesg)
                sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                
                line = wx.StaticLine(self, -1, size=(20,-1),
                                    style=wx.LI_HORIZONTAL)
                sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|
                          wx.RIGHT|wx.TOP, 5)
                
                box = wx.BoxSizer(wx.HORIZONTAL)
                
                btn = wx.Button(self, wx.ID_OK, "Retry")
                btn.SetDefault()
                box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                
                btn = wx.Button(self, wx.ID_CANCEL, "Cancel")
                box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                
                sizer.AddSizer(box, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
                self.SetSizer(sizer);self.SetAutoLayout(True); sizer.Fit(self)

                
        debug( "OpenPort called")
        try:
            self.port = pyxede.Xede(arch.COMM)
            self.port.Connect()
        except (IOError, pyxede.serial.serialutil.SerialException), reason:
            win = OpenFailDialog(self.frame, -1, "Connect Failed",
                                 mesg="Connection Failed: \n%s" % reason)
            self.port = None
            win.CenterOnScreen()
            r = win.ShowModal()
            if r == wx.ID_OK:
                self.OpenPort()
            return

        self.StartEngineMonitor()
        
    #__________________________________________________________________________
    def ClosePort(self, e = None):
        if self.port:
            self.prod.stop()
            if self.port:
                self.port.Disconnect()
            self.port = None
            
            self.menubar.Enable(ID_CONNECT, 1)
            self.menubar.Enable(ID_CONFIG, 1)

            self.menubar.Enable(ID_LOG   , 0)
            self.menubar.Enable(ID_HSLOG , 0)
            self.menubar.Enable(ID_DYNO  , 0)
        
    #__________________________________________________________________________
    def Configure(self,e = None):
        id = 0
        frame = wx.Frame(self.frame, id, title="Settings")
        nb  = wx.Notebook(frame, -1, style = wx.NB_TOP)

        # port settings
        win = wx.Panel(nb, -1)
        nb.AddPage(win, "Port")
        sizer = wx.BoxSizer(wx.VERTICAL)
        id = wx.NewId()
        ports = ['COMM 1', 'COMM 2', 'COMM 3', 'COMM 4',
                 'COMM 5', 'COMM 6', 'COMM 7', 'COMM 8'] 
        rb = wx.RadioBox(win, id, "Choose Serial Port",
                        choices = ports, style = wx.RA_SPECIFY_COLS,
                        majorDimension = 2)
        rb.SetSelection(arch.COMM)
        def set_comport(event):
            arch.SetComm(event.GetInt())
            
            
        wx.EVT_RADIOBOX(self,id, set_comport) 
        sizer.Add(rb, 1, wx.ALL | wx.WEST | wx.EAST | wx.EXPAND, 5)
      
        win.SetSizer(sizer)
        win.SetAutoLayout(True)
        sizer.Fit(win)

        # gnuplot settings
        win = wx.Panel(nb, -1)
        nb.AddPage(win, "Plotting")
        sizer = wx.BoxSizer(wx.VERTICAL)

        #   command
        def fbbc_callback(event):
            arch.SetGnuplotCommand(event.GetString())

        fbbc = FileBrowseButton(win, -1,initialValue = arch.GNUPLOT_CMD,
                                changeCallback = fbbc_callback)
        fbbc.SetLabel("Command:")
        sizer.Add(fbbc, 1, wx.EAST | wx.WEST | wx.EXPAND, 5)

        #   format
        def set_term_txt(event):
            arch.SetGnuplotTerminal(event.GetString())
        def set_term_box(event):
            arch.SetGnuplotTerminal(event.GetString())
            
        line = wx.BoxSizer(wx.HORIZONTAL)
        txt = wx.StaticText(win, -1, "Format ")
        line.Add(txt, 0, wx.EAST | wx.WEST | wx.EXPAND, 0)
        cID = wx.NewId()
        cb = wx.ComboBox(win, cID, arch.GNUPLOT_TERMINAL,
                        choices = arch.GNUPLOT_TERMINALS)
        line.Add(cb, 1, wx.EAST | wx.WEST | wx.EXPAND, 0)
        sizer.Add(line, 0, wx.EAST | wx.WEST | wx.EXPAND, 0)
        wx.EVT_TEXT(    win, cID, set_term_txt)
        wx.EVT_COMBOBOX(win, cID, set_term_box)
        
        #   output
        def fbbo_callback(event):
            arch.GNUPLOT_OUTPUT = event.GetString()

        fbbo = FileBrowseButton(win, -1, initialValue = arch.GNUPLOT_OUTPUT,
                                changeCallback = fbbo_callback)
        fbbo.SetLabel("Output:")
        sizer.Add(fbbo, 1, wx.EAST | wx.WEST | wx.EXPAND, 5)
      

        win.SetSizer(sizer)
        win.SetAutoLayout(True)
        sizer.Fit(win)

        frame.Show(True)
        frame.SetSize((400,200))
    #__________________________________________________________________________

    def RoadDyno(self, start, stop, activedialog,sources,finished):
        self.run = None
        ######################################################################
        # Wait for the the dyno run threshold to be reached
        while self.port.RPM() < start:
            if finished():
                activedialog.EndModal(0)
                return
            
            sleep = arch.time_func()
            while arch.time_func() - sleep < GUI_REFRESH_TIME:
                time.sleep(YIELD_SLEEP_TIME)
            e = UpdateDynoEvent(cur_time = 0.0, RPM = self.port.RPM(),
                                AFR=self.port.AFR(), SK=self.port.SMARTKnock())
            wx.PostEvent(activedialog,e)
        ######################################################################

        # Start "real" run
        data = []
        
        log_evt = threading.Event()

        t = threading.Thread(None, self.port.HighSpeedLog, None,
                             (sources, data),
                             { "finished" : log_evt.isSet } )
        t.start()

        while len(data) < 2 : # wait for first data point
            time.sleep(YIELD_SLEEP_TIME)

        run = dyno.DynoRun()
        
        def parseline(d):
            d = d[-1] # last line
            d = string.split(d, ",")
            return d

        line = parseline(data)
        while int(line[1]) < stop and not finished():
            ctime = float(line[0])
            rpm   = int(line[1])
            sk    = float(line[2])
            afr   = float(line[3]) 
            e = UpdateDynoEvent(cur_time = ctime , RPM = rpm, AFR=afr,
                                SK=sk)
            wx.PostEvent(activedialog,e)
            line = parseline(data)
            
            #update GUI
            sleep = arch.time_func()
            while arch.time_func() - sleep < GUI_REFRESH_TIME:
                time.sleep(YIELD_SLEEP_TIME)                            

            # remove labels
            rundata = data[1:]
            # split lines
            
            for i in range(0, len(rundata)):
                rundata[i] = string.split(rundata[i], ",")
            run.Import(rundata, 1, time_col = 0, knock_col=2,afr_col = 3)
            activedialog.rtplot.Update(run)

        log_evt.set()
 
        t.join()

        self.run = run
        activedialog.EndModal(0)


    def RoadDynoDlg(self, e = None):
        class StartDialog(wx.Dialog):
            def __init__(self, parent, ID, title = "Road Dyno",
                         pos = wx.DefaultPosition,
                         size = wx.DefaultSize, style =wx.DEFAULT_DIALOG_STYLE,
                         mesg = ""):
                
                pre = wx.PreDialog()
                pre.Create(parent, ID, title, pos, size, style)
                self.this = pre.this
                sizer = wx.BoxSizer(wx.VERTICAL)

                box  = wx.BoxSizer(wx.HORIZONTAL)
                txt = wx.StaticText(self, -1, "Start RPM: ")
                self.min = wx.SpinCtrl(self)
                box.Add(txt, 1, wx.ALL, 4)
                box.Add(self.min, 1, wx.ALL, 4)
                sizer.Add(box, 0, wx.EXPAND|wx.EAST|wx.WEST);

                box  = wx.BoxSizer(wx.HORIZONTAL)
                txt = wx.StaticText(self, -1, "Shudown RPM: ")
                self.max = wx.SpinCtrl(self)
                box.Add(txt, 1, wx.ALL, 4)
                box.Add(self.max, 1, wx.ALL, 4)
                sizer.Add(box, 0, wx.EXPAND|wx.EAST|wx.WEST);

                self.min.SetRange(dyno.START_RPM_RANGE[0],
                                  dyno.START_RPM_RANGE[1])
                self.max.SetRange(dyno.SHUTDOWN_RPM_RANGE[0],
                                  dyno.SHUTDOWN_RPM_RANGE[1])

                self.min.SetValue(dyno.ROAD_DYNO_START)
                self.max.SetValue(dyno.ROAD_DYNO_SHUTDOWN)
                self.min.SetToolTip(wx.ToolTip(
                    "Dyno measure begins when this\nRPM is reached." +\
                    "\nRange: %d-%d" %
                    (dyno.START_RPM_RANGE[0],dyno.START_RPM_RANGE[1])))
                self.max.SetToolTip(wx.ToolTip(
                    "Dyno measure completes when this\nRPM is reached." +\
                    "\nRange: %d-%d" %
                    (dyno.SHUTDOWN_RPM_RANGE[0],dyno.SHUTDOWN_RPM_RANGE[1])))

                build_sensor_select(self,sizer, "Aux log variables")

                self.amafi.SetValue(True) # AFR
                self.amapi.SetValue(True) # knock

                self.amafi.Enable(False) # AFR
                self.amapi.Enable(False) # knock


                box  = wx.BoxSizer(wx.HORIZONTAL)

                box.Add(wx.Button(self,wx.ID_OK,     "Start" ),1, wx.ALL, 5)
                box.Add(wx.Button(self,wx.ID_CANCEL, "Cancel"),1, wx.ALL, 5)
                sizer.Add(box, 0);

                self.SetSizer(sizer);self.SetAutoLayout(True);sizer.Fit(self)
        #______________________________________________________________________
        class ActiveDialog(wx.Dialog):
            def __init__(self, parent, ID, title, label,
                         rpm_range, finished,
                         pos = wx.DefaultPosition,
                         size = wx.DefaultSize, style = wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE
                         ,mesg = ""):
                
                pre = wx.PreDialog()
                pre.Create(parent, ID, title, pos, size, style)
                self.this = pre.this
                splitter = wx.SplitterWindow(self, -1)

                panel = wx.Panel(splitter, -1)
                
                sizer = wx.BoxSizer(wx.VERTICAL)

                box  = wx.BoxSizer(wx.HORIZONTAL)
                txt = wx.StaticText(panel, -1, "Start: %d" % rpm_range[0],
                                    style = wx.ALIGN_RIGHT)
                box.Add(txt, 1, wx.ALL, 4)
                txt = wx.StaticText(panel, -1, "Stop: %d" % rpm_range[1],
                                    style = wx.ALIGN_RIGHT)
                box.Add(txt, 1, wx.ALL, 4)
                sizer.Add(box, 0, wx.EXPAND|wx.EAST|wx.WEST);
                hline = wx.StaticLine(panel, -1, size=(20,-1),
                                      style=wx.LI_HORIZONTAL)
                sizer.Add(hline, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|
                          wx.RIGHT|wx.TOP, 5)

                split_labels = string.split(label, ",")
                self.values = []

                font = wx.Font(10, wx.MODERN, wx.NORMAL,
                               wx.NORMAL, False)

                for l in split_labels:
                    box  = wx.BoxSizer(wx.HORIZONTAL)
                    txt = wx.StaticText(panel, -1, "%s: " % l,
                                        style = wx.ALIGN_RIGHT)
                    txt.SetFont(font)
                    box.Add(txt, 1, wx.ALL, 4)
                    txt = wx.StaticText(panel, -1, "0   ")
                    txt.SetFont(font)
                    box.Add(txt, 1, wx.ALL, 4)
                    self.values.append(txt)
                    sizer.Add(box, 0, wx.EXPAND|wx.EAST|wx.WEST);

                def quit_dyno(evt = None):
                    finished.set()

                sizer.Add(wx.Button(panel,wx.ID_CANCEL),0, wx.ALL|wx.ALIGN_BOTTOM, 5)
                wx.EVT_BUTTON(self, wx.ID_CANCEL, quit_dyno)                

                panel.SetSizer(sizer);panel.SetAutoLayout(True);sizer.Fit(panel)

                def update(evt):
                    self.values[0].SetLabel("%.3lf" % evt.cur_time)
                    self.values[1].SetLabel(str(evt.RPM))
                    self.values[2].SetLabel(str(evt.SK))
                    self.values[3].SetLabel(str(evt.AFR))
                    
                EVT_UPDATE_DYNO(self, update)

                self.rtplot = wxdyno.rpmplot.PlottingPanel(splitter,-1)
                splitter.SplitVertically(panel, self.rtplot, 200)

                self.SetSize((800,600))
        #______________________________________________________________________
        
        dlg = StartDialog(self.frame,-1)
        self.prod.stop()            
        if dlg.ShowModal() == wx.ID_OK:
            start = dlg.min.GetValue()
            stop  = dlg.max.GetValue()
            sources, label = dialog_to_sources(dlg)
            
            # dyno dlg
            slabel = label[1:] # remove the comment character
            dyno_evt = threading.Event()
            d = ActiveDialog(self.frame, -1, "Running...", slabel, 
                             (start,stop), dyno_evt )

            t = threading.Thread(None, self.RoadDyno, None,
                             (start, stop, d,sources,dyno_evt.isSet))
            t.start()
            d.ShowModal()
            dyno_evt.set() 
            t.join()
            if self.run:
                 self.dynolist.AddRun(self.run)
                 self.dynolist.Show(True)
                 
        self.StartEngineMonitor()
    #__________________________________________________________________________
    def OnQuit(self,e = None):
        self.ClosePort()
        arch.SaveSettings()
        self.frame.Destroy()

app = MyApp(0)
runs = app.dynolist.runs
app.MainLoop()
