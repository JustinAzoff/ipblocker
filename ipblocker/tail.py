#!/usr/bin/env python
import os
import time

def open_wait(fn):
    while True:
        try:
            f = open(fn)
            return f
        except IOError:
            time.sleep(1)


def tail(fn):
    """Like tail -f """
    last = time.time()

    inode = stat_inode(fn)
    f = open_wait(fn)
    f.seek(0, 2)
    changed = False

    while 1:
        l = f.readline()
        if l:
            yield l
            last = time.time()
        else:
            if changed:
                f.close()
                f = open_wait(fn)
                inode = os.fstat(f.fileno()).st_ino
                changed = False
            if stat_inode(fn) != inode:
                #set changed to true, but then try reading the file more to
                #check to see if it was written to after rotated
                changed = True
            else:
                time.sleep(1)

def stat_inode(fn):
    try :
        return os.stat(fn).st_ino
    except OSError:
        return None

def multitail(filenames):
    files = {}
    for fn in filenames:
        try :
            handle = open(fn)
            handle.seek(0, 2)
            inode = os.fstat(handle.fileno()).st_ino
        except IOError:
            handle = None
            inode = None
        files[fn] = dict(handle=handle, last=0,inode=inode)

    all = files.items()
    while 1:
        read = False
        for fn, info in all:
            l = info['handle'] and info['handle'].readline()
            if l:
                yield fn, l
                info['last'] = time.time()
                info['read'] = read = True
            else:
                info['read'] = False
        for fn, info in all:
            if not info['handle'] or (info['read'] == False and info['inode'] != stat_inode(fn)):
                if info['handle']:
                    info['handle'].close()
                try :
                    info['handle'] = open(fn)
                    info['inode'] = os.fstat(info['handle'].fileno()).st_ino
                except IOError:
                    info['handle'] = None
        if not read:
            time.sleep(1)
