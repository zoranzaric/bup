#!/bin/sh

set -e

usage() {
    echo "Usage: bup delete-commit <branch> <commit>" 1>&2
    exit 1
}

delete() {
    ref=$1
    sha=$2

    GIT_DIR=$BUP_DIR git filter-branch -f --commit-filter "
        if [ \"\$GIT_COMMIT\" = \"$sha\" ]; then
            skip_commit \"\$@\";
        else
            git commit-tree \"\$@\";
        fi" "$ref"
}

main () {
    if [ $# -ne 2 ]; then
        usage
    fi

    ref=$1

    sha=$(git rev-parse $2)
    if [ $? -ne 0 ]; then
        usage
    fi

    delete "$ref" "$sha"

    git repack
}

export GIT_DIR=$BUP_DIR

main "$@"
