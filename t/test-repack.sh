#!/bin/bash

usage() {
    echo "Usage: test-repack.sh <base dir>"
    exit -1
}

TOP="$(/bin/pwd)"
bup()
{
    "$TOP/bup" "$@"
}

if [ $# -ne 1 ]; then
  usage
fi

BASE_DIR=$1
mkdir -p $BASE_DIR

export BUP_DIR=$BASE_DIR/bup
export GIT_DIR=$BUP_DIR
DATA_DIR=$BASE_DIR/data
mkdir -p $DATA_DIR

rm -rf $BASE_DIR/git-fsck.log
rm -rf $BASE_DIR/repack.log
rm -rf $BASE_DIR/runs.log
rm -rf $DATA_DIR/data
rm -rf $BUP_DIR

touch $DATA_DIR/data
bup init

for x in {1..20}; do
  test -f $BASE_DIR/repack.log && mv $BASE_DIR/repack.log $BASE_DIR/repack.log.old
  test -f $BASE_DIR/git-fsck.log && mv $BASE_DIR/git-fsck.log $BASE_DIR/git-fsck.log.lod
  date >> $BASE_DIR/runs.log
  dd if=/dev/urandom bs=100M count=1 >> $DATA_DIR/data
  bup index $DATA_DIR/data
  bup save -n asdf $DATA_DIR/data
  bup repack > $BASE_DIR/repack.log
  git fsck --unreachable > $BASE_DIR/git-fsck.log || break
done
