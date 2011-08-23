% bup-save(1) Bup %BUP_VERSION%
% Zoran Zaric <zz@zoranzaric.de>
% %BUP_DATE%

# NAME

bup-inotify - watch a path recursively and save changes

# SYNOPSIS

bup inotify -n *name* <path>

# DESCRIPTION

`bup inotify` watches a path and saves all changes immediately.

# OPTIONS

-n, --name=*name*
:   the name of the backup set to save to.  See `bup-save`(1)
    for more information


# EXAMPLE

    $ bup inotify -n etc-inotify /etc


# SEE ALSO

`bup-index`(1), `bup-save`(1)

# BUP

Part of the `bup`(1) suite.
