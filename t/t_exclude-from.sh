#!/usr/bin/env bash
. wvtest.sh
#set -e

TOP="$(/bin/pwd)"
export BUP_DIR="$TOP/buptest.tmp"

bup()
{
    "$TOP/bup" "$@"
}

WVSTART "exclude-from"
D=exclude-fromdir.tmp
EXCLUDE_FILE=exclude-from.tmp
echo "$D/d 
 $TOP/$D/g
$D/h" > $EXCLUDE_FILE
rm -rf $D
mkdir $D
export BUP_DIR="$D/.bup"
WVPASS bup init
touch $D/a
WVPASS bup random 128k >$D/b
mkdir $D/d $D/d/e
WVPASS bup random 512 >$D/f
mkdir $D/g $D/h
WVPASS bup index -ux --exclude-from $EXCLUDE_FILE $D
bup save -n exclude-from $D
WVPASSEQ "$(bup ls exclude-from/latest/$TOP/$D/)" "a
b
f"
rm $EXCLUDE_FILE

