#!/usr/bin/env python
import sys, os
from bup import git, options
from bup.helpers import *

optspec = """
bup repack
--
q,quiet    don't show progress meter
n,dry-run  don't do anything, just print what would be done
#,compress=  set compression level to # (0-9, 9 is highest) [1] (See WARNING in manpage!)
"""
o = options.Options(optspec)
(opt, flags, extra) = o.parse(sys.argv[1:])

git.check_repo_or_die()

handle_ctrl_c()

cp = git.CatPipe()

opt.progress = (istty2 and not opt.quiet)
refs = git.list_refs()
refnames = [name for name, sha in refs]

git.lock()

pl = git.PackIdxList(git.repo('objects/pack'))

needed_objects = git.NeededObjects(pl)

# Find needed objects reachable from commits
traversed_objects_counter = 0

for refname in refnames:
    if not refname.startswith('refs/heads/'):
        continue
    log('Traversing %s to find needed objects...\n' % refname[11:])
    for date, sha in ((date, sha.encode('hex')) for date, sha in
                      git.rev_list(refname)):
        for type, sha_ in git.traverse_commit(cp, sha, needed_objects):
            traversed_objects_counter += 1
            qprogress('Traversing objects: %d\r' % traversed_objects_counter)

# Find needed objects reachable from tags
tags = git.tags()
if len(tags) > 0:
    for key in tags:
        log('Traversing tag %s to find needed objects...\n' % ", ".join(tags[key]))
        for type, sha in git.traverse_commit(cp, sha, needed_objects):
            traversed_objects_counter += 1
            qprogress('Traversing objects: %d\r' % traversed_objects_counter)
progress('Traversing objects: %d, done.\n' % traversed_objects_counter)


if traversed_objects_counter == 0:
    o.fatal('No reachable objects found.')


if not opt.dry_run:
    blob_writer = git.PackWriter(compression_level=opt.compress)
    w = git.PackWriter(compression_level=opt.compress)

log('Writing new packfiles...\n')
written_object_counter = 0
for pack in needed_objects.packs:
    ba = needed_objects.get_bitarray_for_pack(pack.name)
    for offset, sha in pack.hashes_sorted_by_ofs():
        idx = pack._idx_from_hash(sha)
        if idx in ba:
            it = iter(cp.get(sha.encode('hex')))
            type = it.next()
            content = "".join(it)
            if not opt.dry_run:
                if type == 'blob':
                    blob_writer._write(sha, type, content)
                else:
                    w._write(sha, type, content)
            needed_objects.remove(sha.encode('hex'))
            written_object_counter += 1
            qprogress('Writing objects: %d\r' % written_object_counter)
    if not opt.dry_run:
        os.unlink(pack.name)
        os.unlink(pack.name[:-3] + "pack")
progress('Writing objects: %d, done.\n' % written_object_counter)

if not opt.dry_run:
    blob_writer.close()
    w.close()

git.unlock()

