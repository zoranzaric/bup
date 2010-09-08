#!/bin/sh
# bup-import-rsnapshot.sh

# Does an import of a rsnapshot archive.

usage() {
    echo "Usage: bup import-rsnapshot <path to rsnapshot's snapshot_root>"
    exit -1
}

[ "$#" -eq 1 ] || usage

if [ ! -e "$1/." ]; then
    echo "$1 isn't a directory!"
    exit -1
fi

ABSPATH=`readlink -f "$1"`

for SNAPSHOT in "$ABSPATH/"*; do
    if [ -e "$SNAPSHOT/." ]; then
        for BRANCH_PATH in "$SNAPSHOT/"*; do
            if [ -e "$BRANCH_PATH/." ]; then
                # Get the snapshot's ctime
                DATE=`stat -c %Z "$BRANCH_PATH"`
                BRANCH=`basename "$BRANCH_PATH"`
                TMPIDX="/tmp/$BRANCH"

                bup index -ux \
                    $BRANCH_PATH/
                bup save \
                    --strip-path=$BRANCH_PATH \
                    --date=$DATE \
                    -n $BRANCH \
                    $BRANCH_PATH/

                if [ -e "$TMPIDX" ]; then
                    rm "$TMPIDX"
                fi
            fi
        done
    fi
done

