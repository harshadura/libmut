#/*******************************************************************************
# * libmut
# * swig/Makefile
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

CC     = gcc
INCS   = -I../ 
CFLAGS = -O3 -DSWIG -fPIC $(INCS)
LD     = ld

SRCS   = ../mut_init.c ../mut_connect.c ../mut_log.c
LIBS   = ../mut_init.o ../mut_connect.o ../mut_log.o



SWIG = swig -I

MACPYDIR = /sw/include/python2.4
MACCFLAGS= -DMAC_OSX $(CFLAGS)
BUNDLELP = /opt/bin/python

LINUXPYDIR=/usr/include/python2.4



osx: python-wrappers $(LIBS)
	$(CC) $(MACCFLAGS) -I$(MACPYDIR) $(LIBS) mut_wrap.c \
         -framework Python -bundle -bundle_loader  /sw/bin/python -o _mut.so 

linux: python-wrappers $(LIBS)
	$(CC) $(LINUXCFLAGS) -c -I$(LINUXPYDIR) $(CFLAGS) mut_wrap.c
	$(LD) -shared $(LIBS) mut_wrap.o -o _mut.so

python-wrappers:
	$(SWIG) $(INCS) -python mut.i 

clean:
	rm -f ./*.o ./*.so mut_wrap.c *.pyc mut.py $(LIBS)