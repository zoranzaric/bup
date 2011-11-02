#!/usr/bin/env python
import sys, os
from bup import git, options
from bup.helpers import *

class NeededObjects():
    def __init__(self, pack_idx_list):
        self.packs = [pack for pack in pack_idx_list.packs
                               if isinstance(pack, git.PackIdx)]
        self.pack_bitarrays = dict()
        for pack in self.packs:
            self.pack_bitarrays[pack.name] = BitArray()

    def __contains__(self, sha):
        for pack in self.packs:
            idx = pack._idx_from_hash(sha.decode('hex'))
            if idx in self.pack_bitarrays[pack.name]:
                return True
        return False

    def add(self, sha):
        for pack in self.packs:
            idx = pack._idx_from_hash(sha.decode('hex'))
            self.pack_bitarrays[pack.name].add(idx)

    def remove(self, sha):
        for pack in self.packs:
            idx = pack._idx_from_hash(sha.decode('hex'))
            self.pack_bitarrays[pack.name].remove(idx)

    def get_bitarray_for_pack(self, name):
        if name in self.pack_bitarrays:
            return self.pack_bitarrays[name]
        else:
            return None

def traverse_commit(cp, sha_hex, needed_objects):
    if sha_hex not in needed_objects:
        needed_objects.add(sha_hex)
        yield ('commit', sha_hex)

        it = iter(cp.get(sha_hex))
        type = it.next()
        assert(type == 'commit')
        tree_sha = "".join(it).split("\n")[0][5:].rstrip(" ")
        for obj in traverse_objects(cp, tree_sha, needed_objects):
            yield obj


def traverse_objects(cp, sha_hex, needed_objects):
    if sha_hex not in needed_objects:
        needed_objects.add(sha_hex)
        it = iter(cp.get(sha_hex))
        type = it.next()

        if type == 'commit':
            yield ('commit', sha_hex)

            tree_sha = "".join(it).split("\n")[0][5:].rstrip(" ")

            for obj in traverse_objects(cp, tree_sha, needed_objects):
                yield obj

        if type == 'tree':
            for (mode,mangled_name,sha) in git.tree_decode("".join(it)):
                yield ('tree', sha_hex)

                for obj in traverse_objects(cp, sha.encode('hex'),
                                            needed_objects):
                    yield obj

        elif type == 'blob':
            yield ('blob', sha_hex)


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

pl = git.PackIdxList(git.repo('objects/pack'))

needed_objects = NeededObjects(pl)

# Find needed objects reachable from commits
traversed_objects_counter = 0

for refname in refnames:
    if not refname.startswith('refs/heads/'):
        continue
    log('Traversing %s to find needed objects...\n' % refname[11:])
    for date, sha in ((date, sha.encode('hex')) for date, sha in
                      git.rev_list(refname)):
        for type, sha_ in traverse_commit(cp, sha, needed_objects):
            traversed_objects_counter += 1
            qprogress('Traversing objects: %d\r' % traversed_objects_counter)

# Find needed objects reachable from tags
tags = git.tags()
if len(tags) > 0:
    for key in tags:
        log('Traversing tag %s to find needed objects...\n' % ", ".join(tags[key]))
        for type, sha in traverse_commit(cp, sha, needed_objects):
            traversed_objects_counter += 1
            qprogress('Traversing objects: %d\r' % traversed_objects_counter)
progress('Traversing objects: %d, done.\n' % traversed_objects_counter)


if traversed_objects_counter == 0:
    o.fatal('No reachable objects found.')


if not opt.dry_run:
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
                w._write(sha, type, content)
            needed_objects.remove(sha.encode('hex'))
            written_object_counter += 1
            qprogress('Writing objects: %d\r' % written_object_counter)
    if not opt.dry_run:
        os.unlink(pack.name)
        os.unlink(pack.name[:-3] + "pack")
progress('Writing objects: %d, done.\n' % written_object_counter)

if not opt.dry_run:
    w.close()

