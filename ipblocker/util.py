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

def country_code(ip):
    import cymruwhois
    c = cymruwhois.Client()
    code = c.lookup(str(ip)).cc
    c.disconnect()
    return code

def lookup_countries(ips):
    import cymruwhois
    c = cymruwhois.Client()
    ret = c.lookupmany_dict(ips)
    c.disconnect()
    return ret
