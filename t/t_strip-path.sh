#!/usr/bin/env bash
. wvtest.sh
#set -e

TOP="$(/bin/pwd)"
export BUP_DIR="$TOP/buptest.tmp"

bup()
{
    "$TOP/bup" "$@"
}

WVSTART "strip-path"
D=strip-path.tmp
rm -rf $D
mkdir $D
export BUP_DIR="$D/.bup"
WVPASS bup init
touch $D/a
WVPASS bup random 128k >$D/b
mkdir $D/d $D/d/e
WVPASS bup random 512 >$D/f
WVPASS bup index -ux $D
bup save --strip-path $TOP -n strip-path $D
WVPASSEQ "$(bup ls strip-path/latest/$D/)" "a
b
d/
f"

