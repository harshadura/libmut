#!/bin/bash

TMPDIR_PARENT=/tmp/tmp-dist-libmut
TMPDIR=$TMPDIR_PARENT/libmut

function very_clean (){
 find $1 -type d -name ".deps" -exec rm -r {} \;
 rm -rf $1/autom4te.cache
 rm -f  $1/config.log $1/config.status
 find $1 -name "Makefile" -exec rm  {} \;
 find $1 -name "*~" -exec rm -i {} \;
 rm -f  $1/autogen.sh $1/very_clean.sh

}

./autogen.sh
mkdir -p   $TMPDIR
cp -a .    $TMPDIR/
very_clean $TMPDIR


FILENAME=`pwd`/../libmut-dist-`date  +%m-%d-%Y`.tar.gz
cd $TMPDIR_PARENT && tar cvfz $FILENAME libmut
rm -rf $TMPDIR_PARENT