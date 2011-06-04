#!/usr/bin/env python
import stat
from bup import client, git, options, vfs
from bup.helpers import *

def send_objects(objects):
    stats = dict()
    stats['commit'] = 0
    stats['tree'] = 0
    stats['blob'] = 0
    stats['outbytes'] = 0

    if opt.verbose:
        log("Pushing:\n")
    for type, sha in objects:
        (new_sha, outbytes) = send_object(type, sha, None)
        stats[type] += 1
        stats['outbytes'] += outbytes

    if opt.verbose:
        log("Transmitted:\n"
            "  %d commits\n"
            "  %d trees\n"
            "  %d blobs\n"
            "  %d bytes\n\n" % (stats['commit'],
                                stats['tree'],
                                stats['blob'],
                                stats['outbytes']))

    return new_sha

def send_object(type, sha, shalist):
    outbytes_last = w.outbytes

    if opt.verbose >= 2:
        log("%s %s " % (sha, type))
    if not w.exists(sha.decode('hex')):
        if type == 'commit' or type == 'tree':
            if not opt.dry_run:
                it = iter(cp.get(sha))
                assert(it.next()==type)
                content = "\n".join(it)
                new_sha = w._write(sha.decode('hex'), type, content)
        else:
            if not opt.dry_run:
                it = iter(cp.get(sha))
                assert(it.next()==type)
                blob = "".join(it)
                new_sha = w._write(sha.decode('hex'), type, blob)
        if opt.verbose >= 2:
            log("tranmitted %d bytes\n" % (w.outbytes - outbytes_last))
    else:
        new_sha = None
        if opt.verbose >= 2:
            log("already exists\n")

    return (new_sha, (w.outbytes - outbytes_last))


optspec = """
bup push <names...>
--
r,remote=  hostname:/path/to/repo of remote repository
v,verbose  increase log output (can be used more than once)
n,dry-run  just print what would be done
all        push all backup sets
"""
o = options.Options(optspec)
(opt, flags, extra) = o.parse(sys.argv[1:])

if not opt.remote:
    o.fatal("-r has to be set")

git.check_repo_or_die()

handle_ctrl_c()

cp = git.CatPipe()

refnames = []
if all:
    refs = git.list_refs()
    refnames = [name for name, sha in refs]
else:
    for rename in extra:
        refnames.append('refs/heads/%s' % opt.name)

for refname in refnames:
    cli = client.Client(opt.remote)
    oldref = refname and cli.read_ref(refname) or None
    w = cli.new_packwriter()

    lst = [obj for obj in cp.traverse_ref(refname)]

    known_shas = set()
    unique = []
    for type, sha in lst:
        if sha not in known_shas:
            known_shas.add(sha)
            unique.append((type, sha))

    lst = [x for x in reversed(unique)]

    if opt.verbose:
        stats = dict()
        stats['commit'] = 0
        stats['tree'] = 0
        stats['blob'] = 0
        stats['outbytes'] = 0

        log("%d local objects:\n" % len(lst))
        for type, sha in lst:
            stats[type] += 1
            if opt.verbose >= 2:
                log("%s %s\n" % (sha, type))
        log("  %d commits\n"
            "  %d trees\n"
            "  %d blobs\n" % (stats['commit'],
                              stats['tree'],
                              stats['blob']))
        log("\n")

    head_sha = send_objects(lst)

    w.close()
    if head_sha:
        cli.update_ref(refname, head_sha, oldref)

