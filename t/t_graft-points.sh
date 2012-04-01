#!/usr/bin/env bash
. wvtest.sh
#set -e

TOP="$(/bin/pwd)"
export BUP_DIR="$TOP/buptest.tmp"

bup()
{
    "$TOP/bup" "$@"
}

WVSTART "graft-points"
D=graft-points.tmp
rm -rf $D
mkdir $D
export BUP_DIR="$D/.bup"
WVPASS bup init
touch $D/a
WVPASS bup random 128k >$D/b
mkdir $D/d $D/d/e
WVPASS bup random 512 >$D/f
WVPASS bup index -ux $D
bup save --graft $TOP/$D=/grafted -n graft-point-absolute $D
WVPASSEQ "$(bup ls graft-point-absolute/latest/grafted/)" "a
b
d/
f"
bup save --graft $D=grafted -n graft-point-relative $D
WVPASSEQ "$(bup ls graft-point-relative/latest/$TOP/grafted/)" "a
b
d/
f"

