#/*******************************************************************************
# * libmut
# * swig/python_test.py
# *
# * Copyright 2006 Donour sizemore (donour@unm.edu)
# *  
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# ******************************************************************************/

import sys
import time

import mut


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print "Usage: python_test device"
        sys.exit(-1)

    dev = sys.argv[1]
    print "MUT Protocol Test ~~ python ~~:", dev  
    print "---------------------------------------------"

    conn = mut.mut_connect_posix(dev)
    if(not conn):
        print dev, "failed"
        sys.exit(-1)

    rc = mut.mut_init(conn)
    if(rc):
        print "Init failed"
        sys.exit(-1)

    for i in range(0,100):
        rpm    = mut.MUTRPM(conn)
        kc     = mut.MUTKNOCKSUM(conn)
        octane = mut.MUTOCTANENUM(conn)
        timing = mut.MUTTIMING(conn)
        print "RPM:", rpm, "\tknocksum:", kc, "\toctane:", octane, "\ttiming:", timing 
        time.sleep(0.05) # you could also use: mut.mut_msleep(100)

    mut.mut_free(conn)
