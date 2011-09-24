#!/usr/bin/env python
import sys, os
from bup import git, options
from bup.helpers import *

class Db():
    def __init__(self):
        import sqlite3
        if os.path.isfile(os.path.expanduser('~/.bup/gc.sqlite')):
            os.unlink(os.path.expanduser('~/.bup/gc.sqlite'))
        self.con = sqlite3.connect(os.path.expanduser('~/.bup/gc.sqlite'))
        sql = "CREATE TABLE needed_shas (sha string)"
        self.con.execute(sql);

    def __iter__(self):
        sql = "SELECT sha FROM needed_shas;"
        cursor = self.con.execute(sql)
        for (sha,) in cursor:
            yield str(sha).decode('hex')

    def __contains__(self, sha):
        sql = "SELECT * FROM needed_shas WHERE sha IN(?);"
        cursor = self.con.execute(sql, (sha.encode('hex'),))
        try:
            cursor.next()
            return True
        except StopIteration:
            return False

    def add(self, sha):
        if sha not in self:
            sql = "INSERT INTO needed_shas VALUES (?);"
            self.con.execute(sql, (sha.encode('hex'),))
            self.con.commit()


class NeededObjects():
    def __init__(self, pack_idx_list):
        self.pack_idx_list = pack_idx_list
        self.pack_bitarrays = dict()
        for pack in self.pack_idx_list.packs:
            self.pack_bitarrays[pack.name] = BitArray()

    def __contains__(self, sha):
        for pack in self.pack_idx_list.packs:
            idx = pack._idx_from_hash(sha.decode('hex'))
            if idx in self.pack_bitarrays[pack.name]:
                return True
        return False

    def add(self, sha):
        for pack in self.pack_idx_list.packs:
            idx = pack._idx_from_hash(sha.decode('hex'))
            self.pack_bitarrays[pack.name].add(idx)

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
        tree_sha = "".join(it).split("\n")[0].lstrip("tree ").rstrip(" ")
        for obj in traverse_objects(cp, tree_sha, needed_objects):
            yield obj


def traverse_objects(cp, sha_hex, needed_objects):
    if sha_hex not in needed_objects:
        needed_objects.add(sha_hex)
        it = iter(cp.get(sha_hex))
        type = it.next()

        if type == 'commit':
            yield ('commit', sha_hex)

            tree_sha = "".join(it).split("\n")[0].lstrip("tree ").rstrip(" ")

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
bup purge [-f] [-n]
--
f,force    don't ask, just do it
n,name=    name of backup set to purge from (if any specific)
d,dry-run  don't do anything, just print what would be done
c,commit   purge a specific commit
v,verbose  increase log output (can be used more than once)
q,quiet    don't show progress meter
#,compress=  set compression level to # (0-9, 9 is highest) [1]
"""
o = options.Options(optspec)
(opt, flags, extra) = o.parse(sys.argv[1:])

git.check_repo_or_die()

handle_ctrl_c()

cp = git.CatPipe()

opt.progress = (istty2 and not opt.quiet)
if opt.name:
    refnames = ['refs/heads/%s' % opt.name]
else:
    refs = git.list_refs()
    refnames = [name for name, sha in refs]

pl = git.PackIdxList(git.repo('objects/pack'))

needed_objects = NeededObjects(pl)

# Find needed objects reachable from commits
for refname in refnames:
    if not refname.startswith('refs/heads/'):
        continue
    log('Traversing %s to find needed objects...\n' % refname[11:])
    traversed_objects_counter = 0
    for date, sha in cp.get_commits(refname):
        for type, sha_ in traverse_commit(cp, sha, needed_objects):
            traversed_objects_counter += 1
            qprogress('Traversing objects: %d\r' % traversed_objects_counter)
qprogress('Traversing objects: %d, done.\n' % traversed_objects_counter)

# Find needed objects reachable from tags
tags = git.tags()
if len(tags) > 0:
    for key in tags:
        log('Traversing tag %s to find needed objects...\n' % ", ".join(tags[key]))
        for type, sha in traverse_commit(cp, sha, needed_objects):
            traversed_objects_counter += 1
            qprogress('Traversing objects: %d\r' % traversed_objects_counter)
qprogress('Traversing objects: %d, done.\n' % traversed_objects_counter)

blob_writer = git.PackWriter(compression_level=opt.compress)
w = git.PackWriter(compression_level=opt.compress)

log('Writing new packfiles...\n')
written_shas = set()
written_object_counter = 0
for pack in pl.packs:
    ba = needed_objects.get_bitarray_for_pack(pack.name)
    for offset, sha in pack.hashes_sorted_by_ofs():
        idx = pack._idx_from_hash(sha)
        if idx in ba:
            if not sha in written_shas:
                it = iter(cp.get(sha.encode('hex')))
                type = it.next()
                content = "".join(it)
                if type == 'blob':
                    blob_writer._write(sha, type, content)
                else:
                    w._write(sha, type, content)
                written_shas.add(sha)
                written_object_counter += 1
                qprogress('Writing objects: %d\r' % written_object_counter)
    os.unlink(pack.name)
    os.unlink(pack.name[:-3] + "pack")
progress('Writing objects: %d, done.\n' % written_object_counter)

w.close()

