#!/bin/sh

usage () {
    echo "Usage: bup delete <first commit> [<last commit>]"
    exit -1
}

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    usage
    exit 1
fi

first="$1"
if [ $# = "2" ]; then
    last="$2"
else
    last="$1"
fi

child=$(git rev-list HEAD | grep -B1 "$last" | grep -v "$last")
parent=$(git rev-parse "$first^")

if [ -e ".git/info/grafts" ]; then
    mv .git/info/grafts .git/info/grafts.backup
fi

echo "$child $parent" > .git/info/grafts

git filter-branch

if [ -e ".git/info/grafts.backup" ]; then
    mv .git/info/grafts.backup .git/info/grafts
fi

