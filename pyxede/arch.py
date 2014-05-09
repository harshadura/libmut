############################################################################
#
# arch.py
#
# Copyright 2005-6 Donour Sizemore (donour@cs.uchicago.edu)
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

__version__ = string.split('$Revision: 1.3 $')[1]
__date__ = string.join(string.split('$Date: 2006/02/09 17:24:22 $')[1:3], ' ')
__author__ = ('C. Donour Sizemore <donour@cs.uchicago.edu>',)

PYXEDE_CONFIG_FILE = "pyxede.cfg"

import ConfigParser
cfg  = ConfigParser.RawConfigParser()
cfg.read(PYXEDE_CONFIG_FILE)


WINDOWS_REFRESH  = -1
GNUPLOT_TERMINAL = cfg.get("gnuplot", "terminal")
TMPDIR           = cfg.get("gnuplot", "tmpdir")
GNUPLOT_CMD      = cfg.get("gnuplot", "command")
GNUPLOT_OUTPUT   = ""
GNUPLOT_TERMINALS= ["aqua", "windows", "x11", "postscript","pdf", "png"]

WXVERSION        = int(cfg.get("wx", "wxversion"))

COMM = int(cfg.get("port", "comm"))

import time
time_func = time.time

import sys
if sys.platform == "darwin":
    GNUPLOT_TERMINAL = cfg.get("gnuplot", "mac_terminal")
    WXVERSION = int(cfg.get("wx", "mac_wxversion"))

if sys.platform == 'win32':
    WINDOWS_REFRESH = 1
    GNUPLOT_TERMINAL = cfg.get("gnuplot", "win_terminal")
    GNUPLOT_CMD = cfg.get("gnuplot", "win_command")
    WXVERSION = int(cfg.get("wx", "win_wxversion"))
    
    time_func = time.clock
    time.clock()  # get the clock started for subsequent calls
    
    ver = sys.getwindowsversion()
    if ver[0] == 5 and ver[1] == 0: # windows 2000
        TMPDIR = cfg.get("gnuplot", "winxp_tmpdir")
    else:
        TMPDIR = cfg.get("gnuplot", "win2k_tmpdir")


def SetGnuplotTerminal(t):
    global GNUPLOT_TERMINAL
    GNUPLOT_TERMINAL = t

    if sys.platform == "darwin":
        cfg.set("gnuplot", "mac_terminal", t)
    elif sys.platform == "win32":
        cfg.set("gnuplot", "win_terminal", t)
    else:
        cfg.set("gnuplot", "terminal", t)


def SetGnuplotCommand(c):
    global GNUPLOT_CMD 
    GNUPLOT_CMD = c

    if sys.platform == "darwin":
        cfg.set("gnuplot", "mac_command", c)
    elif sys.platform == "win32":
        cfg.set("gnuplot", "win_command", c)
    else:
        cfg.set("gnuplot", "command", c)


def SetComm(c):
    global COMM
    COMM = c
    cfg.set("port", "comm", str(c))

def SaveSettings():
    f = file(PYXEDE_CONFIG_FILE, "w")
    cfg.write(f)


if __name__ == "__main__":
    print "Version: ", __version__
    print "Detected: ", sys.platform
    print "Using gnuplot terminal: ", GNUPLOT_TERMINAL
    print "tmp directory: ", TMPDIR
    print "Windows Refresh style: ", WINDOWS_REFRESH

