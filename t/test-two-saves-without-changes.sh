#!/usr/bin/env bash
. ./wvtest-bup.sh

set -e -o pipefail

WVSTART 'all'

top="$(pwd)"
tmpdir="$(wvmktempdir)"
export BUP_DIR="$tmpdir/bup"

bup() { "$top/bup" "$@"; }

mkdir "$tmpdir/foo"
touch "$tmpdir/foo/baz"
WVPASS bup init
WVPASS bup index "$tmpdir/foo"
WVPASS bup save -n foo "$tmpdir/foo"
WVPASSEQ "$(git fsck --unreachable)" ""
WVPASS bup index "$tmpdir/foo"
WVPASS bup save -n foo "$tmpdir/foo"
WVPASSEQ "$(git fsck --unreachable)" ""

rm -rf "$tmpdir"
