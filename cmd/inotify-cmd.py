#!/usr/bin/env python
import pyinotify
import os
import sys

from bup import git, options, index, save, metadata

BUP_DIR = os.environ.get('BUP_DIR')

optspec = """
bup inotify [-n name] <paths...>
--
n,name=    name of backup set to update (defaults to inotify)
"""

o = options.Options(optspec)
(opt, flags, extra) = o.parse(sys.argv[1:])

if opt.name:
    name = opt.name
else:
    name = "inotify"

git.check_repo_or_die()

wm = pyinotify.WatchManager()

mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY

def backup(path):
    metadata_path = os.path.join(path, ".bup.meta")
    metadata_file_handler = open(metadata_path, 'w')
    metadata.save_tree(output_file=metadata_file_handler,
                       paths=[path],
                       recurse=True,
                       write_paths=True,
                       save_symlinks=True,
                       xdev=False)
    index.index(paths=[path])
    save.save(quiet=True, name = name, paths=[path])
    os.unlink(metadata_path)

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        if not event.pathname.endswith(".bup.meta"):
            print "Creating:", event.pathname
            # TODO new directories should be added to the watchlist
            backup(event.pathname)

    def process_IN_DELETE(self, event):
        if not event.pathname.endswith(".bup.meta"):
            print "Removing:", event.pathname
            # if a file or directory is deleted we have to index and save its
            # parent
            backup(os.path.join(event.pathname, os.path.pardir))

    def process_IN_MODIFY(self, event):
        if not event.pathname.endswith(".bup.meta"):
            print "Modifying:", event.pathname
            backup(event.pathname)

handler = EventHandler()
notifier = pyinotify.Notifier(wm, handler, timeout=10)
for path in extra:
    wm.add_watch(path, mask, rec=True, auto_add=True)
    backup(path)

notifier.loop()

