#!/usr/bin/env bash
. wvtest.sh
#set -e

TOP="$(/bin/pwd)"
export BUP_DIR="$TOP/buptest.tmp"

bup()
{
    "$TOP/bup" "$@"
}

WVSTART "compression"
D=compression0.tmp
export BUP_DIR="$TOP/$D/.bup"
rm -rf $D
mkdir $D
WVPASS bup init
WVPASS bup index $TOP/Documentation
WVPASS bup save -n compression -0 --strip $TOP/Documentation
# 'ls' on NetBSD sets -A by default when running as root, so we have to undo
# it by grepping out any dotfiles.  (Normal OSes don't auto-set -A, but this
# is harmless there.)
WVPASSEQ "$(bup ls compression/latest/ | sort)" \
	 "$(ls $TOP/Documentation | grep -v '^\.' | sort)"
COMPRESSION_0_SIZE=$(du -s $D | cut -f1)

D=compression9.tmp
export BUP_DIR="$TOP/$D/.bup"
rm -rf $D
mkdir $D
WVPASS bup init
WVPASS bup index $TOP/Documentation
WVPASS bup save -n compression -9 --strip $TOP/Documentation
WVPASSEQ "$(bup ls compression/latest/ | sort)" "$(ls $TOP/Documentation | sort)"
COMPRESSION_9_SIZE=$(du -s $D | cut -f1)

WVPASS [ "$COMPRESSION_9_SIZE" -lt "$COMPRESSION_0_SIZE" ]

