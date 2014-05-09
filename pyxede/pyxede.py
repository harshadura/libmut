#!/usr/bin/env python
############################################################################
#
# pyxede.py
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
#
# This is the main library interface for communicating with an Xede.
#
############################################################################

import string
__version__ = string.split('$Revision: 1.12 $')[1]
__date__ = string.join(string.split('$Date: 2006/02/11 03:22:55 $')[1:3], ' ')
__author__ = ('C. Donour Sizemore <donour@cs.uchicago.edu>',)

CMD_CANCEL_ALL    = 0xFD
CMD_START         = 0xF8
CMD_CONNECT       = 0xA6
CMD_WRITE_POINT   = 0xA4
CMD_READ_POINT    = 0xA5
CMD_READ_BYTE     = 0xA0
CMD_READ_IO_POINT = 0xAC
CMD_SELECT        = 0xAE

RESPONSE_OK       = 0xE1

# High Speed logging sources
LOG_TIME           = 0x0001
LOG_RPM	           = 0x0002
LOG_ANALOG_MAP_IN  = 0x0004
LOG_ANALOG_MAF_IN  = 0x0008
LOG_TPS_IN         = 0x0010
LOG_FREQ_MAF_IN    = 0x0020
LOG_ANALOG_MAP_OUT = 0x0040
LOG_ANALOG_MAF_OUT = 0x0080
LOG_TPS_OUT        = 0x0100
LOG_FREQ_MAF_OUT   = 0x0200
LOG_WGSOL_OUT      = 0x0400
LOG_INJ0_OUT       = 0x0800
LOG_INJ1_OUT       = 0x1000
LOG_TIMING_OUT     = 0x2000
#LOG_FLAGS      = 0x4000 # b0: Mark (uses map bank select in,
#                        #     disables it's normal function)
SOURCE_MARKER      = 0x8000
FLAGS_MARK         = 0x01
FLAGS_KNOCK        = 0x02
FLAGS_SPRAY        = 0x04

TIMESTAMP_DELTA = 0.01 # in seconds

SAMPLERATE_FREQ = 50 # how often (in lines) samplerate is computed

LCMAX = 22.39
LCMIN = 7.35

def LC1_Normalize(v):
    """Convert 0-100% value read from LC-1 Wideband O2 sensor and covert it to
    A:F ratio. WARNING: for LC-1, 50% is NOT stoichiometric for gasoline."""

    if v < 1 :
        print "Skeptical LC-1 value converted"
    v = v / 100.0
    delta = LCMAX - LCMIN
    afr = v*delta + LCMIN
    return afr

INPUT_NAMES = {
    "AN0" : "SMART Knock",
    "AN1" : "Air fuel ratio"
    }
     


import time
import serial
from io_array import IO_ARRAY
import dyno

#______________________________________________________________________________
class Xede:
    """Xede device connection

    This object is used for all communication with connected an Xede
    piggyback engine management system"""

    #__________________________________________________________________________
    def __init__(self, portnum):
        """Initialize Xede

        Required argument is the port number 0 .. N
        """

        # Fixme: These should be user configurable
        baud     = 115200
        databits = 8
        par      = serial.PARITY_NONE # parity
        sb       = 1                  # stopbits
        to       = 2                  # timeout in seconds
        
        self.port = serial.Serial(portnum, baud, \
           parity = par, stopbits = sb, bytesize = databits, timeout = to)
                                  
    #__________________________________________________________________________
    def send_command(self, cmd):
        """Send and verify a single command

        The protocol specifies that the reponse to commands should begin with
        the inverse (not quite specified) of the command itself. If you send
        CMD_START, the Xede should respond with -CMD_START.
        """
        
        cmds = chr(cmd)
        self.port.write(cmds)
        r = self.port.read(1)
        if len(r) == 0:
            raise IOError, "No response from device"

        r = ord(r)
        if r + cmd != 255:
            raise IOError, "Send/Recieve mismatch"
        
    #__________________________________________________________________________
    def Connect(self):
        """Initialize conection to Xede

        Send CMD_START and CMD_CONNECT to Xede and verify response. Xede
        should then be in a state to start manipulating maps or reading i/o
        array data"""

        self.send_command(CMD_START)
        self.send_command(CMD_CONNECT)
        
        return 0

    #__________________________________________________________________________
    def Disconnect(self):
        """Disconnect from the Xede and close port

        """
        self.port.close()

    #__________________________________________________________________________
    def sensor(self, sid):
        """Get specified sensor value from i/o array

        """
 
        if sid >= 0 and sid < len(IO_ARRAY):
            cmd = chr(CMD_START) + chr(CMD_READ_IO_POINT) + chr(sid) + \
                  chr(0) + chr(0)

            self.port.write(cmd)
            r = self.port.read(6)
            if len(r) != 6:
                raise IOError, "I/O Array response incorrect"

            low  = r[4]
            high = r[5]
             
            r = (ord(high) << 8) + ord(low)
            return r
        else:
            raise IOError,  "Invalid Sensor: %d" % sid
    #__________________________________________________________________________
    def RPM(self):
        """Get Engine RPM

        """
        r = self.sensor(0)
        return r

    #__________________________________________________________________________
    def CAS(self):
        """Get crank angle sensor value (-128 : 128)
                
        """
        r = self.sensor( 1)
        r = r - 128
        return r
    
    #__________________________________________________________________________
    def AnalogTPSIn(self):
        """Get analog throttle position input (0.0 - 100.0 %)
                
        """
        r = self.sensor( 4)
        r = r / 10.0
        return r

    #__________________________________________________________________________
    def AnalogTPSOut(self):
        """Get analog throttle position output (0.0 - 100.0 %)
                
        """
        r = self.sensor( 13)
        r = r / 10.0
        return r
    #__________________________________________________________________________
    def AnalogMAPIn(self):
        """Get analog MAP input duty cycle (0.0 - 100.0 %)
                
        """
        r = self.sensor( 2)
        r = r / 10.0
        return r

    #__________________________________________________________________________
    def AnalogMAPOut(self):
        """Get analog MAP output duty cycle (0.0 - 100.0 %)
                
        """
        r = self.sensor( 11)
        r = r / 10.0
        return r

    #__________________________________________________________________________
    def AnalogMAFIn(self):
        """Get analog MAF input duty cycle (0.0 - 100.0 %)
                
        """
        r = self.sensor( 3)
        r = r / 10.0
        return r

    #__________________________________________________________________________
    def AnalogMAFOut(self):
        """Get analog MAF output duty cycle (0.0 - 100.0 %)
                
        """
        r = self.sensor( 12)
        r = r / 10.0
        return r

    #__________________________________________________________________________
    def BoostIDC(self):
        """Get Boost input duty cycle (0.0 - 100.0 %)
                
        """
        r = self.sensor( 6)
        r = r / 10.0
        return r

    #__________________________________________________________________________
    def BoostODC(self):
        """Get Boost output duty cycle (0.0 - 100.0 %)
                
        """
        r = self.sensor( 17)
        r = r / 10.0
        return r

    #__________________________________________________________________________
    def Knock(self):
        """Get knock state (0 = not attenuated, 1 = attenuated)

        """
        r = self.sensor( 16)
        return r

    #__________________________________________________________________________
    def FreqMAFIn(self):
        """Get frequency sampled MAF input duty cycle (0.0 - 100.0 %)
                
        """
        r = self.sensor( 24)
        r = r / 10.0
        return r

    #__________________________________________________________________________
    def FreqMAFOut(self):
        """Get frequency sampled MAF input duty cycle (0.0 - 100.0 %)
                
        """
        r = self.sensor( 25)
        r = r / 10.0
        return r

    #__________________________________________________________________________
    def CurrentMap(self):
        """Get id of currently loaded map/bank (0/1).

        """

        r = self.sensor(28)
        # FIXME: bit 15 is the changing map flag
        r = r & 0x7FFF
        return r

    #__________________________________________________________________________
    def AFR(self):
        """Get Wideband A/F reading from S.M.A.R.T defined signal AN1. Value is
        converted to 'real' A:F based on the LC-1 sensor range.
        """
        v = self.AnalogMAFIn()
 #       v = LC1_Normalize(v)
        return v
    #__________________________________________________________________________
    def SMARTKnock(self):
        """Get S.M.A.R.T knock level.
        """
        return self.AnalogMAPIn()

    #__________________________________________________________________________
    def HighSpeedLog(self, sources, dest,
                     finished = lambda : True,
                     iterations = 0,
                     sample_rate = None):
        """The HighSpeedLog functions provides access to a special feature of
        the Xede that allows logging IO Array values much faster than manually
        sampling.

        Mandatory Arguments:

        sources: Specify which values you want to log by bitwise OR'ing the
                 LOG_* flags that are global to this module. For example if you
                 want to log the duty cycles of injectors 0 and 1, you pass
                 LOG_INJ0_OUT | LOG_INJ1_OUT. Note that RPM is _always_ logged
                 so passing it is redundant.

        Optional Arguments:

        dest: This controls where the logged data is stored. If dest is a file
              (or anything else with a 'write' function), the log data will be
              written with the objects write function. If dest is a list, data
              will be appended to this list -- one comma delimited line at a
              time. Otherwise, a TypeError will be thrown.
        
        There are two ways to control logging. If both are given, logging
        continues until _both_ conditions are met.
        
        iterations: number of times to sample given sources
        finished: This should be a callable object (function). When calling
                  this object returns True, logging terminates. Useful to
                  control logging from a seperate thread.

        sample_rate: This should be a reference to store the sample rate.
                     If defined, it will be called, periodically, with the
                     current sample rate as its only argument.
        """

        if hasattr(dest, "write") and hasattr(dest.write, "__call__"):
            log_func = dest.write
        elif type(dest) == list:
            log_func = dest.append
        else:
            raise TypeError, "Log destination of unknown type: " + type(dest)

        START_LOG = 0x01
        STOP_LOG  = 0x00

        SOURCES = SOURCE_MARKER | \
                  LOG_TIME      | \
                  LOG_RPM       | \
                  sources

        SOURCES = chr((SOURCES >> 8)) + chr(SOURCES & 0xFF)

        # Start logging
        cmd = chr(CMD_START)        + \
              chr(CMD_SELECT)       + \
              chr(START_LOG)        + \
              SOURCES               

        self.port.write(cmd)

        #FIXME: we should check the return values here

        # Write list of labels
        line = "# Time, RPM"
        if sources & LOG_ANALOG_MAP_IN:
            an0_in = ord(self.port.read(1)) / 255.0 *  100.0
            line = line + ", %s" % INPUT_NAMES['AN0']
                
        if sources & LOG_ANALOG_MAF_IN:
            an1_in = ord(self.port.read(1)) / 255.0 *  100.0
            line = line + ", %s" % INPUT_NAMES['AN1']
                
        if sources & LOG_TPS_IN:
            an2_in = ord(self.port.read(1)) / 255.0 *  100.0
            line = line + ", TPS_IN"
                
        if sources & LOG_FREQ_MAF_IN:
            freq0_in = ord(self.port.read(1)) / 255.0 *  100.0
            line = line + ", FreqMAFIn"
                                
        if sources & LOG_ANALOG_MAP_OUT:
            an0_out = ord(self.port.read(1)) / 255.0 *  100.0
            line = line + ", AnalogMAPOut"

        if sources & LOG_ANALOG_MAF_OUT:
            an1_out = ord(self.port.read(1)) / 255.0 *  100.0
            line = line + ", AnalogMAFOut"

        if sources & LOG_TPS_OUT:
            an2_out = ord(self.port.read(1)) / 255.0 *  100.0
            line = line + ", TPS_OUT"

        if sources & LOG_FREQ_MAF_OUT:
            freq0_out = ord(self.port.read(1)) / 255.0 *  100.0
            line = line + ", FreqMAFOut"

        if sources & LOG_TIMING_OUT:
            shift_out = ord(self.port.read(1)) - 128
            line = line + ", Timing"
                
        if sources & LOG_WGSOL_OUT:
            wgsol_out = ord(self.port.read(1)) / 255.0 *  100.0
            line = line + ", WGSOL_OUT"
            # FIXME: the title of wgsol needs to be resolved
        if sources & LOG_INJ0_OUT:
            inj0_out = ord(self.port.read(1))
            line = line + ", Inj0_Out"
        if sources & LOG_INJ1_OUT:
            inj1_out = ord(self.port.read(1))
            line = line + ", Inj1_Out"
        log_func(line + "\n")
    
        # Collect log values
        lines_received = 0
        last_sr_time = time.time()
        while not finished() or iterations > 0:

            # All sample rate computions are here.
            if sample_rate != None:
                if lines_received >= SAMPLERATE_FREQ:
                    elap_time = time.time() - last_sr_time
                    sample_rate(int(lines_received / elap_time))
                    lines_received = 0
                    last_sr_time = time.time()
                else:
                    lines_received = lines_received + 1
                    
            if iterations > 0:
                iterations  = iterations - 1

            marker = self.port.read(1)
            while 1: # find marker
                old = marker
                marker = self.port.read(1)
                if ord(old) == 0x01 and ord(marker) == 0xFE:
                    break
                else:
                    print "missed one"

            def str2_to_int(s):
                return (ord(s[0]) << 8) + ord(s[1])

            ts = self.port.read(2)
            timestamp = str2_to_int(ts)
            timestamp = timestamp * TIMESTAMP_DELTA

            r = self.port.read(2)
            rpm = str2_to_int(r)

            line = "%.3lf, %d" % (timestamp, rpm)

            if sources & LOG_ANALOG_MAP_IN:
                an0_in = ord(self.port.read(1)) / 255.0 *  100.0
                line = line + ", %.1f" % an0_in
                
            if sources & LOG_ANALOG_MAF_IN:
                an1_in = ord(self.port.read(1)) / 255.0 *  100.0
                an1_in = LC1_Normalize(an1_in)
                line = line + ", %.1f" % an1_in
                
            if sources & LOG_TPS_IN:
                an2_in = ord(self.port.read(1)) / 255.0 *  100.0
                line = line + ", %.1f" % an2_in
                
            if sources & LOG_FREQ_MAF_IN:
                freq0_in = ord(self.port.read(1)) / 255.0 *  100.0
                line = line + ", %.1f" % freq0_in
                                
            if sources & LOG_ANALOG_MAP_OUT:
                an0_out = ord(self.port.read(1)) / 255.0 *  100.0
                line = line + ", %.1f" % an0_out

            if sources & LOG_ANALOG_MAF_OUT:
                an1_out = ord(self.port.read(1)) / 255.0 *  100.0
                line = line + ", %.1f" % an1_out

            if sources & LOG_TPS_OUT:
                an2_out = ord(self.port.read(1)) / 255.0 *  100.0
                line = line + ", %.1f" % an2_out

            if sources & LOG_FREQ_MAF_OUT:
                freq0_out = ord(self.port.read(1)) / 255.0 *  100.0
                line = line + ", %.1f" % freq0_out

            if sources & LOG_TIMING_OUT:
                shift_out = ord(self.port.read(1)) - 128
                line = line + ", %d" % shift_out
                
            if sources & LOG_WGSOL_OUT:
                wgsol_out = ord(self.port.read(1)) / 255.0 *  100.0
                line = line + ", %.1f" % wgsol_out
                
            if sources & LOG_INJ0_OUT:
                inj0_out = ord(self.port.read(1))
                line = line + ", %d" % inj0_out
            if sources & LOG_INJ1_OUT:
                inj1_out = ord(self.port.read(1))
                line = line + ", %d" % inj1_out

            log_func(line + "\n")
            if type(dest) == file:
                dest.flush()
                
        # Stop logging
        cmd = chr(CMD_START)        + \
              chr(CMD_SELECT)       + \
              chr(STOP_LOG)         + \
              SOURCES               + \
              chr(CMD_CANCEL_ALL)    
        self.port.write(cmd)

        # FIXME: figure out what is sent here
        r = "stop"
        while len(r) > 0:
            r = self.port.read()

        return dest
#_ end of library ____________________________________________________________ 

def test_high_speed_log():
    import threading
    x=Xede(0)
    x.Connect()
    print x.HighSpeedLog(LOG_TIMING_OUT| LOG_ANALOG_MAF_IN,[], iterations = 50)
    print x.RPM()
    print x.HighSpeedLog(LOG_ANALOG_MAP_IN | LOG_WGSOL_OUT ,[], iterations = 5)
    x.Disconnect()
    
def test_comms():
    x=Xede(0)
    x.Connect()
    print "Connected to Xede. Current Map: ", x.CurrentMap()
    while 1:
        print "%d %d %f %f %f %f %f %f" % (x.CurrentMap(), x.RPM() ,
                               x.AnalogMAFIn(), x.AnalogMAFOut(),
                               x.BoostODC(), x.BoostIDC(),
                               x.FreqMAFIn(), x.FreqMAFOut())

def test_afr():
    x=Xede(0)
    x.Connect()
    print "Connected to Xede. Current Map: ", x.CurrentMap()
    while 1:
        print "%d: %f, %f" % (x.RPM(), x.AFR(), x.SMARTKnock())
        
            

def test_read_map():
    x=Xede(0)
    x.Connect()
    print "Connected to Xede. Current Map: ", x.CurrentMap()

    map = []
    for i in range(0,255):

        cmd = chr(CMD_START) + chr(0xa0) + chr(0xd0) + chr(i) + chr(0)
        self.port.write(cmd)
        r = self.port.read(5)
        if len(r) != 5:
            raise IOError, "I/O Array response incorrect"
        map.append(int(r[4]))


if __name__ == "__main__":
    test_afr()
