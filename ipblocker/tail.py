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
            time.sleep(5)
            if time.time() - last > 120 and getsize() < size:
                f.close()
                f = open(fn)
