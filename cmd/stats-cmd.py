#!/usr/bin/env python
import sys, os, sqlite3
from bup import git, options
from bup.helpers import *

git.check_repo_or_die()

db_path = git.repo('bupstats.sqlite3')

if os.path.exists(db_path):
    os.unlink(db_path)

db = sqlite3.connect(db_path)
db.execute('CREATE TABLE objects (sha text, size integer);')
db.execute('CREATE TABLE refs (a text, b text);')

DONT_SKIP_KNOWN = False

def traverse_commit(cp, sha_hex, needed_objects):
    if sha_hex not in needed_objects or DONT_SKIP_KNOWN:
        needed_objects.add(sha_hex)

        it = iter(cp.get(sha_hex))
        type = it.next()
        assert(type == 'commit')
        content = "".join(it)
        tree_sha = content.split("\n")[0][5:].rstrip(" ")
        db.execute('INSERT INTO refs VALUES (?,?)', (sha_hex, tree_sha))
        sum = len(content)
        for (t,s,c,l) in traverse_objects(cp, tree_sha, needed_objects):
            sum += c
            yield (t,s,c,l)
            db.execute('INSERT INTO objects VALUES (?,?)', (s, c))
        yield ('commit', sha_hex, sum, len(content))
        db.execute('INSERT INTO objects VALUES (?,?)', (sha_hex, sum))


def traverse_objects(cp, sha_hex, needed_objects):
    if sha_hex not in needed_objects or DONT_SKIP_KNOWN:
        needed_objects.add(sha_hex)
        it = iter(cp.get(sha_hex))
        type = it.next()

        if type == 'commit':

            content = "".join(it)
            yield ('commit', sha_hex, len(content))
            tree_sha = content.split("\n")[0][5:].rstrip(" ")

            for obj in traverse_objects(cp, tree_sha, needed_objects):
                yield obj

        if type == 'tree':
            content = "".join(it)
            sum = len(content)
            for (mode,mangled_name,sha) in git.tree_decode(content):
                db.execute('INSERT INTO refs VALUES (?,?)', (sha_hex, sha.encode('hex')))

                for (t,s,c,l) in traverse_objects(cp, sha.encode('hex'),
                                            needed_objects):
                    sum += c
                    yield (t,s,c,l)
            yield ('tree', sha_hex, sum, len(content))

        elif type == 'blob':
            content = "".join(it)
            yield ('blob', sha_hex, len(content), len(content))

optspec = """
bup stats
--
q,quiet    don't show progress meter
"""
o = options.Options(optspec)
(opt, flags, extra) = o.parse(sys.argv[1:])

handle_ctrl_c()

cp = git.CatPipe()

opt.progress = (istty2 and not opt.quiet)
refs = git.list_refs()
refnames = [name for name, sha in refs]

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
        for type, sha_, sum, size in traverse_commit(cp, sha, needed_objects):
            sys.stdout.write("%s\t%s\t%d\t%d\n" % (type, sha_, sum, size))
            traversed_objects_counter += 1
            qprogress('Traversing objects: %d\r' % traversed_objects_counter)

# Find needed objects reachable from tags
tags = git.tags()
if len(tags) > 0:
    for key in tags:
        log('Traversing tag %s to find needed objects...\n' % ", ".join(tags[key]))
        for type, sha, sum, size in traverse_commit(cp, sha, needed_objects):
            sys.stdout.write("%s\t%s\t%d\t%d\n" % (type, sha_, sum, size))
            traversed_objects_counter += 1
            qprogress('Traversing objects: %d\r' % traversed_objects_counter)
progress('Traversing objects: %d, done.\n' % traversed_objects_counter)


if traversed_objects_counter == 0:
    o.fatal('No reachable objects found.')

db.commit()
