def groupby(it, keyfunc):
    """Like itertools.groupby, but don't require a sorted list"""
    ret = {}
    for x in it:
        key = keyfunc(x)
        ret.setdefault(key, []).append(x)
    return ret.items()

def subnet(ip):
    """1.2.3.4 -> 3"""
    return (ip.int()/256)&255
