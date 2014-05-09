############################################################################
#
# gnuplot.py
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
#
# Routines for accessing gnuplot to generate plots
#
############################################################################
import string
__version__ = string.split('$Revision: 1.1.1.1 $')[1]
__date__ = string.join(string.split('$Date: 2005/07/28 15:33:16 $')[1:3], ' ')
__author__ = ('C. Donour Sizemore <donour@cs.uchicago.edu>',)


import os
import datetime
import arch

PLOT_FORMAT = 'set xlabel "RPM" ;'                  +\
              'set mxtics 4 ;'                      +\
              'set mytics 2 ;'                      +\
              'set key left top box ;'              +\
              'set grid xtics mxtics ytics mytics ;'


def plot(data, labels = [], terminal=arch.GNUPLOT_TERMINAL,
         output = arch.GNUPLOT_OUTPUT, command = arch.GNUPLOT_CMD, title = None):
    """Plot data with gnuplot. Data should be a list of list of tuples (i.e.
    list of X,Y plots).

    Optional Arguments:

    labels:   can be used to specify the labels for plots.
    terminal: can be used to set the terminal type if desired.
    output: gnuplot output (probably want to specify a file here)
    command: gnuplot command 

    """

    PLOT_CMD = "plot "
    if title:
        global PLOT_FORMAT
        PLOT_FORMAT = PLOT_FORMAT + "set title \"%s\" ;" % title
        
    files = []
    for k in range(0,len(data)):
        d = data[k]

        tfile = arch.TMPDIR+ "pyxede.tmp.%d" % k
        files.append(tfile)

        f = open(tfile, "w")
        for i in d:
            print >>f, i[0], "\t", i[1]
        f.close()

        if k>0:
            PLOT_CMD  = PLOT_CMD + ","
        PLOT_CMD = PLOT_CMD + " '"+ tfile + "' "  + " with lines "

        if len(labels) > k:
            PLOT_CMD = PLOT_CMD + " title " + " '%s' " % labels[k]

    
    # FIXME: this should all be in arch.py
    import sys

    if sys.platform == "win32" or 0:
        cmdfilename = arch.TMPDIR+"pyxede_gnuplot.cmd"
        cmdfile = open(cmdfilename, "w")
        print >>cmdfile, "set terminal %s" % terminal
        print >>cmdfile, PLOT_FORMAT
        if output:
            print >>cmdfile, "set output '%s'" %  output
        print >>cmdfile, PLOT_CMD
        cmdfile.flush(); cmdfile.close()
        os.system(command + " -persist "+ cmdfilename) 
        
    else:
        pid = os.fork()
        if pid == 0:
            pipe = os.popen(command, 'w')
        
            print >>pipe, "set terminal %s" % terminal
            print >>pipe, PLOT_FORMAT
            if output:
                print >>pipe, "set output '%s'" %  output
            print >>pipe, PLOT_CMD
            pipe.flush()
            pipe.close()

            for f in files:
                os.unlink(f)
    
            sys.exit(0)

    
def test():
    """Test function, not a public interface"""
    print "Testing gnuplot"

    d = [(1,1), (2,2), (3,2.1), (4, 2.5)]
    m = [(1,2), (2,-2), (3,2.5), (4, 27.5)]
    plot([d,m])

    #plot([m,d], ["two","one"], "postscript", "test.ps")


if __name__ == "__main__":
    test()

