#!/usr/bin/env bash
. wvtest.sh
#set -e

TOP="$(/bin/pwd)"
export BUP_DIR="$TOP/buptest.tmp"

bup()
{
    "$TOP/bup" "$@"
}

WVSTART "indexfile"
D=indexfile.tmp
INDEXFILE=tmpindexfile.tmp
rm -f $INDEXFILE
rm -rf $D
mkdir $D
export BUP_DIR="$D/.bup"
WVPASS bup init
touch $D/a
touch $D/b
mkdir $D/c
WVPASS bup index -ux $D
bup save --strip -n bupdir $D
WVPASSEQ "$(bup ls bupdir/latest/)" "a
b
c/"
WVPASS bup index -f $INDEXFILE --exclude=$D/c -ux $D
bup save --strip -n indexfile -f $INDEXFILE $D
WVPASSEQ "$(bup ls indexfile/latest/)" "a
b"

