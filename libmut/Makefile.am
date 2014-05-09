## Makefile.am -- Process this file with automake to produce Makefile.in

SUBDIRS = . tools

MUT_SRC=mut.h mut_connect.c mut_init.c mut_log.c

bin_PROGRAMS = mut_test 
lib_LIBRARIES = libmut.a

libmut_a_SOURCES = $(MUT_SRC)
mut_test_SOURCES = mut_test.c $(MUT_SRC)



