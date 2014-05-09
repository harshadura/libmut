############################################################################
#
# io_array.py
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

IO_ARRAY = [
    ("Engine RPM"                           ,"100rpm resolution"),
    ("Crank timing out (tuned timing shift)","0 = -max?; 128 = 0?; 255 = +max?"),
    ("Analog 0 input (MAP)"                 ,"0..1000 = 0..100.0% of full scale (5V),"),
    ("Analog 1 input (MAF)"                 ,"0..1000 = 0..100.0% of full scale (5V),"),
    ("Analog 2 input (TPS)"                 ,"0..1000 = 0..100.0% of full scale (5V),"),
    ("(unused)"                             ,"" ),
    ("Boost solenoid input duty cycle"      ,"0..1000 = 0..100.0% duty cycle (active low),"),
    ("Reserved / temporary input 0"         , "" ),
    ("Reserved / temporary input 1"         , "" ),
    ("Reserved / temporary input 2"         , "" ),
    ("Reserved / temporary input 3"         , "" ),
    ("Analog 0 output (MAP) tuned"          ,"0..1000 = 0..100.0% of full scale (5V),"),
    ("Analog 1 output (MAF) tuned"          ,"0..1000 = 0..100.0% of full scale (5V),"),
    ("Analog 2 output (TPS) tuned"          ,"0..1000 = 0..100.0% of full scale (5V),"),
    ("Injector channel 0 output pulse width","0..255 = 0..25.5ms on-time"),
    ("Injector channel 1 output pulse width","0..255 = 0..25.5ms on-time"),
    ("Knock attenuate state"                ,"0 = not attenuated, 1 = attenuated"),
    ("Boost solenoid output duty cycle"     ,"0..1000 = 0..100.0% duty cycle (active low),"),
    ("Internal 3.3V power supply"           ,"675 = 3.3V (approximately),"),
    ("Internal 5.0V power supply"           ,"512 = 5.0V (approximately),"),
    ("Input power supply voltage"           ,"491 = 12V (approximately),"),
    ("Timing logic version"                 , "" ),
    ("Timing logic build"                   , "" ),
    ("Timing logic track ID"                , "" ),
    ("MAF input percentage (frequency MAF)" ,"0..1000 = 0..100.0%"),
    ("MAF output percentage (frequency MAF)","0..1000 = 0..100.0%"),
    ("Water spray state"                    ,"0 = not activated, 1 = activated"),
    ("Tuning data checksum"                 ,"Periodically updated (1-2 seconds),"),
    ("Map info"                             , "Low byte = current map bank number Bit 15 = 'changing map banks' flag")
    ]

if __name__ == "__main__":
    for i in range(0, len(IO_ARRAY)):
        print "%d:\t%s\n\t%s" % (i, IO_ARRAY[i][0], IO_ARRAY[i][1])
