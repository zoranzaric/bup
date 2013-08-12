#!/usr/bin/env bash
. ./wvtest-bup.sh

set -e -o pipefail

WVSTART 'all'

top="$(pwd)"
tmpdir="$(wvmktempdir)"
export BUP_DIR="$tmpdir/bup"

bup() { "$top/bup" "$@"; }

mkdir "$tmpdir/foo"

bup index "$tmpdir/foo" &> /dev/null
WVPASSEQ "$?" "15"

rm -rf "$tmpdir"
