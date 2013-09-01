#!/usr/bin/env bash
. ./wvtest-bup.sh

set -e -o pipefail

WVSTART 'save remote'

top="$(pwd)"
tmpdir="$(wvmktempdir)"
export BUP_DIR="$tmpdir/bup"

bup() { "$top/bup" "$@"; }

mkdir "$tmpdir/data"
touch "$tmpdir/data/foo"

set +e
bup init
bup index "$tmpdir/data" &> /dev/null
WVPASS bup save -r :$BUP_DIR -n r-test $tmpdir/data
