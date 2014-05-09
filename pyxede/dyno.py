############################################################################
#
# dyno.py
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
__version__ = string.split('$Revision: 1.10 $')[1]
__date__ = string.join(string.split('$Date: 2006/02/10 00:13:10 $')[1:3], ' ')
__author__ = ('C. Donour Sizemore <donour@cs.uchicago.edu>',)

import gnuplot
import arch
import math
from threading import Thread
from xedecsv import read_csv

# default road dyno limit parameters in RPM
START_RPM_RANGE    = (1000, 5000)
SHUTDOWN_RPM_RANGE = (2000, 9000)
ROAD_DYNO_START    = 1200
ROAD_DYNO_SHUTDOWN = 2000

#______________________________________________________________________________
class DynoRun:
    """The DynoRun should be used to represent a single road-dyno-type power
    measurement.

    """
    def __init__(self, data = []):
        """Init function.

        data argument is a list 4-tuples of (rpm, torque, power,afr).
        """
        self.data = data
        
    #__________________________________________________________________________
    def SetData(self, data):
        self.data = data

    #__________________________________________________________________________
    def torque(self):
        """Get list of tuples (rpm, torque)

        """
        t = []
        for d in self.data:
            t.append( (d[0], d[1]))

        return t

    #__________________________________________________________________________
    def hp(self):
        """Get list of tuples (rpm, power)

        """
        h = []
        for d in self.data:
            h.append( (d[0], d[2]))

        return h

    #__________________________________________________________________________
    def afr(self):
        """Get list of tuples (rpm, afr)

        """
        a = []
        for d in self.data:
            a.append( (d[0], d[3]))

        return a
    #__________________________________________________________________________
    def knock(self):
        """Get list of tuples (rpm, knock)

        """
        a = []
        for d in self.data:
            a.append( (d[0], d[4]))

        return a

    #__________________________________________________________________________
    def timing_shift(self):
        """Get list of tuples (rpm, timing shift)

        """
        a = []
        for d in self.data:
            a.append( (d[0], d[5]))

        return a
    #__________________________________________________________________________
    def trim(self, size = None, threshold = None):
        """Trim data points given certain parameters.

           keyword arguments:

           size: trim size number of sample from the beginning and end of
                 data.
           threshold: trim all torque values above threshold.
        
        """
        if size:
            if 2*size >0 and len(self.data) > 2*size:
                self.data = self.data[size:-size]
        elif threshold:
            data = []
            for d in self.data:
                if d[1] < threshold:
                    data.append(d)
            self.data = data
        
    #__________________________________________________________________________
    def torque_area(self):
        """Calculate torque 'area under the curve' using simple, uniform width
           numerical intergration.

        """
        t = self.torque()
        total = 0.0
        for i in range(0, len(t)):
            width = t[i][0] - t[i-1][0]
            height= t[i][1]
            if width != 0:
                total = total + height*width
        return total
    #__________________________________________________________________________
    def hp_area(self):
        """Calculate power 'area under the curve' using simple, uniform width
           numerical intergration.

        """
        hp = self.hp()
        total = 0.0
        for i in range(0, len(hp)):
            width = hp[i][0] - hp[i-1][0]
            height= hp[i][1]
            if width != 0:
                total = total + height*width
        return total
    #__________________________________________________________________________
    def Load(self, filename):
        """Load DynoRun from a text file.

        The file format specifices that lines beginning with '#' will be
        comments and that each line shall contain at least 3, comma delimited,
        numerical values.

        value 1: rpm
        value 2: torque
        value 3: rpm
        value 4: afr
        value 5: knock

        """
        data = read_csv(filename)
        t = []
        for line in data:
            if len(line) != 6:
                raise IOError, "Invalid file format"
            t.append( (int(line[0]),  float(line[1]),
                       float(line[2]),float(line[3]),
                       float(line[4]),float(line[5])
                       ))
                    
        self.data = t
        
    #__________________________________________________________________________
    def Save(self, filename):
        """Save a DynoRun to a file.

        """
        f = open(filename, "w")

        print >>f, "# pyXede Dyno Run, %d samples" % len(self.data)
        print >>f, "#RPM,\tTorque,\tPower,\tA/F,\tKnock,\tTimingShift"
        for d in self.data:
            print >>f, "%.5d,\t%.3f,\t%.3f,\t%.3f,\t%.3f,\t%.3f" % \
                        (d[0],   d[1],  d[2],  d[3],  d[4],d[5])

        f.close()
        
    #__________________________________________________________________________
    def Import(self,input, rpm_col,
               time_col   = None,
               sample_rate= None,
               torque_col = None,
               power_col  = None,
               afr_col    = None,
               knock_col  = None,
               ts_col     = None
               ):

        """Import arbitrary data in list of tuples form. A number of parameters
           are available to specify what is represented in the tuples.

           (mandatory)
           rpm_col: specify which element of the tuple contains RPM value

           (optional)
           time_col: specify column contains timestamps used for dRPM torque
                     calculation
           sample_rate: samplerate of data
           torque_col: if torque is available in data, specify it here
           power_col: if power is available in data, specify it here
           afr_col: specify location of wideband afr readings
           knock_col: specify location of s.m.a.r.t style knock values
           ts_col: specify timing shift location

        """
        #FIXME: power_col doesn't work

        if time_col==None and sample_rate==None and torque_col == None:
            raise SyntaxError, \
                    "Must set either time_col, sample_rate, or torque_col"

        data = []

        # pass one, fill in rpm and AFR if they are available
        for i in range(0, len(input)):
            line = input[i]
            rpm = int(line[rpm_col])

            if afr_col == None:
                afr = 0.0
            else:
                try:
                    afr = float(line[afr_col])
                except ValueError, m:
                    afr = 0.0
                    print "Bad AFR value (%s)" % m

            if knock_col == None:
                knock = 0.0
            else:
                try:
                    knock = float(line[knock_col])
                except ValueError, m:
                    knock = 0.0
                    print "Bad knock value (%s)" % m

            if ts_col == None:
                ts = 0.0
            else:
                try:
                    ts = float(line[ts_col])
                except ValueError, m:
                    ts = 0.0
                    print "Bad timing shift value (%s)" % m

            data.append( [rpm, 0.0, 0.0, afr,knock,ts] )
                
        # pass one, fill in torque and power
        # FIXME: missing 1st entry of torque and power
        for i in range(1, len(input)):
            if torque_col != None:
                torque = float(input[i][torque_col])
            elif time_col != None:
                if input[i][time_col] == input[i-1][time_col]:
                    continue
                    #FIXME:raise ValueError, "Identical timestamps at %d" %i

                dRPM =float(input[i][rpm_col ]) - float(input[i-1][rpm_col ])
                dtime=float(input[i][time_col]) - float(input[i-1][time_col])
                torque = dRPM/dtime
                        
            elif sample_rate != None:
                torque = (data[i][0] - data[i-1][0])*sample_rate

            data[i][1] = torque
            if power_col != None:
                power = float(input[i][power_col])
            else:
                power = torque*data[i][0] / 5252
            data[i][2] = power

            #FIXME: check that power = rpm*torque/5252

        self.data = []
        for i in range(0,len(data)):
             #FIXME: dropping rpms make no sense!
             if len(self.data) == 0 or data[i][0] >= self.data[-1][0]:
                 self.data.append(data[i])

    #________________________________________________________________________
    def gnuplot(self, cmd = arch.GNUPLOT_CMD, terminal=arch.GNUPLOT_TERMINAL,
             output = arch.GNUPLOT_OUTPUT, title = None):
        """Plot rpm vs. torque and rpm vs. power using gnuplot.

        Optional arguments are:
        terminal: gnuplot terminal
        output: gnuplot output
        cmd: gnuplot command

        """
        gnuplot.plot([self.torque(), self.hp()],
                     ["Torque", "Power"], terminal, output, cmd, title=title)
        
    #__________________________________________________________________________
    def Smooth(self, func, kargs  = {}):
        """Smooth the dyno data using given func
        
        """

        t = func(self.torque(), **kargs)
        if len(t) != len(self.data):
            raise "Smoothing Error"

        new_data = []
        for i in range(0,len(self.data)):
            # FIXME: smoothing might move RPM points on afr
            rpm = self.data[i][0]
            torque = t[i][1]
            afr   = self.data[i][3]
            knock = self.data[i][4]
            shifted_timing = self.data[i][5]
            
            new_data.append( (rpm, torque, rpm*torque / 5252,
                              afr,knock,shifted_timing) )

        self.data = new_data

#______________________________________________________________________________
class Car:
    def __init__(self):
        self.gear_ratios = [ 999.9, # 0th gear :)
                             2.928,
                             1.950,
                             1.407,
                             1.031,
                             0.720,
                             ]
        self.fd_ratio     = 4.529
        self.mass         = 1395   # in kg
        self.wheel_radius = 0.323  # in meters

    def ERPM_to_WRPM(self, rpm, gear):
        r = rpm / self.gear_ratios[gear]
        r = r   / self.fd_ratio 
        return r

    def RPM_to_Speed(self, rpm, gear):
        """Return speed (m/s) from engine RPM


        """        
        # calculate meters/min
        r = self.ERPM_to_WRPM(rpm, gear)
        r = r  * (self.wheel_radius *2) * math.pi # 2*pi*r
        # get SI base units (m/s)
        r = r / 60.0
        return r

    def A_to_Torque(self, start_speed, end_speed, etime, gear):
        accel = ( end_speed-start_speed ) / etime
        force = self.mass * accel
        # FIXME: account of air resistance
        torque = force * self.wheel_radius
        torque = torque / self.fd_ratio / self.gear_ratios[gear]
        return torque

    def dRPM_to_Torque(self, start_rpm, end_rpm, etime, gear):
        start_speed = self.RPM_to_Speed(start_rpm, gear)
        end_speed   = self.RPM_to_Speed(end_rpm, gear)

        t = self.A_to_Torque(start_speed, end_speed, etime, gear)
        return t


def test_import():
    data = read_csv("UTEC.csv")
    d = DynoRun()
    d.Import(data, 0,sample_rate = 5, afr_col=12)

    data = read_csv("smart2.csv")
    d = DynoRun()
    d.Import(data, 1,time_col = 0, afr_col=3)

    data = read_csv("smart_smooth.csv")
    d = DynoRun()
    d.Import(data, 0,torque_col = 1)
    
def test_smooth():
    d = DynoRun()
    d.Load("dustin.csv")
    import smooth
    d.Smooth(smooth.SavGol)
    d.trim()
    d.gnuplot()
    d = DynoRun()
    d.Load("dustin.csv")
    import smooth
    d.Smooth(smooth.NNA)
    d.trim()
    d.gnuplot()

if __name__ == "__main__":
    test_import()

    
