#!/usr/bin/env bash
. wvtest.sh
#set -e

TOP="$(/bin/pwd)"
export BUP_DIR="$TOP/buptest.tmp"

bup()
{
    "$TOP/bup" "$@"
}

WVSTART "import-rsnapshot"
D=rsnapshot.tmp
export BUP_DIR="$TOP/$D/.bup"
rm -rf $D
mkdir $D
WVPASS bup init
mkdir -p $D/hourly.0/buptest/a
touch $D/hourly.0/buptest/a/b
mkdir -p $D/hourly.0/buptest/c/d
touch $D/hourly.0/buptest/c/d/e
WVPASS true
WVPASS bup import-rsnapshot $D/
WVPASSEQ "$(bup ls buptest/latest/)" "a/
c/"

