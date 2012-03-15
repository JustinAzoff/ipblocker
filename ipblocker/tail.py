#!/usr/bin/env python
import os
import time
def tail(fn):
    """Like tail -f """
    last = time.time()

    getsize = lambda: os.stat(fn).st_size
    size = getsize()
    f = open(fn)
    f.seek(0, 2)

    while 1:
        l = f.readline()
        if l:
            yield l
            last = time.time()
            size = getsize()
        else:
            time.sleep(1)
            if time.time() - last > 120 and getsize() < size:
                f.close()
                f = open(fn)

def stat_size(fn):
    return os.stat(fn).st_size

def multitail(filenames):
    files = {}
    for fn in filenames:
        handle = open(fn)
        handle.seek(0, 2)
        files[fn] = dict(handle=handle, last=0,size=0)

    all = files.items()
    while 1:
        read = False
        for fn, info in all:
            l = info['handle'].readline()
            if l:
                yield fn, l
                info['last'] = time.time()
                info['size'] = stat_size(fn)
                read = True
        if not read:
            time.sleep(1)
        for fn, info in all:
            if time.time() - info['last'] > 20 and stat_size(fn) < info['size']:
                info['handle'].close()
                info['handle'] = open(fn)
            
