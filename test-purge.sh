#!/usr/bin/env bash
. wvtest.sh
#set -e

TOP="$(/bin/pwd)"
export BUP_DIR="$TOP/buptest.tmp"

bup()
{
    "$TOP/bup" "$@"
}

# Create a purge test tree.
(
    rm -rf "$TOP/buppurge.tmp/src"
    mkdir -p "$TOP/buppurge.tmp/src"
    cp -a Documentation cmd lib t "$TOP/buppurge.tmp"/src
) || WVFAIL

WVSTART 'purge - general'

# Create source bupdir
rm -rf "$TOP/buppurge.tmp/.bup"
bup -d "$TOP/buppurge.tmp/.bup" init

# Index and save test tree to source bupdir
bup -d "$TOP/buppurge.tmp/.bup" index -ux "$TOP/buppurge.tmp/src"
bup -d "$TOP/buppurge.tmp/.bup" save --strip -n purge "$TOP/buppurge.tmp/src"
bup -d "$TOP/buppurge.tmp/.bup" tag foo purge

sleep 3

bup -d "$TOP/buppurge.tmp/.bup" index -ux "$TOP/buppurge.tmp/src"
bup -d "$TOP/buppurge.tmp/.bup" save --strip -n purge "$TOP/buppurge.tmp/src"

WVPASSEQ $(ls "$TOP/buppurge.tmp/.bup/objects/pack" | grep "pack$" | wc -l) "2"
WVPASSEQ $(bup -d "$TOP/buppurge.tmp/.bup" ls purge/ | wc -l) "4"
bup -d "$TOP/buppurge.tmp/.bup" purge
WVPASSEQ $(ls "$TOP/buppurge.tmp/.bup/objects/pack" | grep "pack$" | wc -l) "1"
WVPASSEQ $(bup -d "$TOP/buppurge.tmp/.bup" ls purge/ | wc -l) "4"

