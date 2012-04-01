#!/usr/bin/env bash
. wvtest.sh
#set -e

TOP="$(/bin/pwd)"
export BUP_DIR="$TOP/buptest.tmp"

bup()
{
    "$TOP/bup" "$@"
}

WVSTART "exclude-bupdir"
D=exclude-bupdir.tmp
rm -rf $D
mkdir $D
export BUP_DIR="$D/.bup"
WVPASS bup init
touch $D/a
WVPASS bup random 128k >$D/b
mkdir $D/d $D/d/e
WVPASS bup random 512 >$D/f
WVPASS bup index -ux $D
bup save -n exclude-bupdir $D
WVPASSEQ "$(bup ls exclude-bupdir/latest/$TOP/$D/)" "a
b
d/
f"

