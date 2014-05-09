CC     = gcc
CFLAGS = -Wall -O3
LD     = ld

SWIG = swig

PYINC    = /usr/include/python2.4
MACPYDIR = /System/Library/Frameworks/Python.framework/Versions/2.3
BUNDLELP = /usr/bin/python

mac: savgol_wrapper rpmplot_wrapper
	$(CC) -I$(MACPYDIR)/Headers -framework Python -bundle -bundle_loader $(MACPYDIR)/bin/python savgol.c savgol_wrap.c  -o _savgol.so

	$(CC) -I$(MACPYDIR)/Headers -framework Python -bundle -bundle_loader $(MACPYDIR)/bin/python crpmplot.c crpmplot_wrap.c  -o _crpmplot.so

savgol_wrapper:
	$(SWIG) -python savgol.i

rpmplot_wrapper:
	$(SWIG) -python crpmplot.i

linux: savgol_wrapper

	$(CC) $(CFLAGS) -c savgol.c savgol_wrap.c -I$(PYINC)
	$(LD) -shared savgol.o savgol_wrap.o -o _savgol.so 
test: linux
	python test.py >test.python
	echo 'plot "test.python" using 1:2, "test.python" using 1:3 with lines' \
             | gnuplot -persist

install:
	cp _savgol.so ../ 
	cp savgol.py ../
clean:
	rm -rf *.o *.so *_wrap.c
	rm -rf savgol*.py savgol.pyc
	rm -rf crpmplot*.py crpmplot.pyc
	rm -rf test