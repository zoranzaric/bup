% bup-push(1) Bup %BUP_VERSION%
% Zoran Zaric <zz@zoranzaric.de>
% %BUP_DATE%

# NAME

bup-push - transfer backup sets to a remote server

# SYNOPSIS

bup push [-v] -r *host*:*path* <names...>

# DESCRIPTION

Use `bup push` to transfer one or more backup sets to the given remote server.

# OPTIONS

-r, --remote=*host*:*path*
:   push the backup set to the given remote server.  If
    *path* is omitted, uses the default path on the remote
    server (you still need to include the ':')

-v, --verbose
:   increase verbosity (can be used more than once).  With
    one -v, prints statistics.  With two -v, also prints
    every object.

--all
:   push all local backup sets to the remote

# EXAMPLE

    # transfer the local backup set *my-pc-backup*
    # to the server *myserver*
    $ bup push -r myserver: my-pc-backup

    # transfer all local backup sets to the server *myserver*
    $ bup push -r myserver: --all

# SEE ALSO

`bup-save`(1)

# BUP

Part of the `bup`(1) suite.
