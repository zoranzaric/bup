#!/usr/bin/env bash
. wvtest.sh
#set -e

TOP="$(/bin/pwd)"
export BUP_DIR="$TOP/buptest.tmp"

bup()
{
    "$TOP/bup" "$@"
}

WVSTART "exclude"
D=exclude.tmp
rm -rf $D
mkdir $D
export BUP_DIR="$D/.bup"
WVPASS bup init
touch $D/a
WVPASS bup random 128k >$D/b
mkdir $D/d $D/d/e
WVPASS bup random 512 >$D/f
WVPASS bup index -ux --exclude $D/d $D
bup save -n exclude $D
WVPASSEQ "$(bup ls exclude/latest/$TOP/$D/)" "a
b
f"
mkdir $D/g $D/h
WVPASS bup index -ux --exclude $D/d --exclude $TOP/$D/g --exclude $D/h $D
bup save -n exclude $D
WVPASSEQ "$(bup ls exclude/latest/$TOP/$D/)" "a
b
f"

