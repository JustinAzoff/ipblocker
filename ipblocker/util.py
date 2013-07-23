from ipblocker.config import config
def groupby(it, keyfunc):
    """Like itertools.groupby, but don't require a sorted list"""
    ret = {}
    for x in it:
        key = keyfunc(x)
        ret.setdefault(key, []).append(x)
    return ret.items()


def num_subnets(flows):
    by_dst = util.groupby(flows, lambda a: util.subnet(a['dstip']))
    return len(list(by_dst))


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

def ip_summary(flows):
    ips = {}
    for f in flows:
        s = f['srcip']
        d = f['dstip']
        r = ips.setdefault(s, {})
        if not r:
            r['num_flows'] = 1
            r['subnets'] = set()
            r['start_flows'] = []
            r['stop_flows'] = []
        else:
            r['num_flows'] +=1
            r['subnets'].add(subnet(d))

        if len(r['start_flows']) < 5:
            r['start_flows'].append(f)

        if r['num_flows'] > 5:
            r['stop_flows'] = r['stop_flows'][-4:] + [f]

    for ip, data in ips.iteritems():
        data['num_subnets'] = len(data['subnets'])
    return ips

def wakeup_backend():
    return False
    wakeup_host = config.get('db','host')
    import tcpsleep
    return tcpsleep.client.wakeup(host=host, port=11112)


def window(d,slice=5):
    """Generate sublists from a real list

        >>> list(window(range(10),11))
        [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]
        >>> list(window(range(10),9))
        [[0, 1, 2, 3, 4, 5, 6, 7, 8], [9]]
        >>> list(window(range(10),5))
        [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]
        >>> list(window(range(10),3))
        [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
        >>> list(window(range(10),1))
        [[0], [1], [2], [3], [4], [5], [6], [7], [8], [9]]

    """
    for x in xrange(0,len(d),slice):
        a=x
        b=x+slice
        yield d[a:b]

time_suffixes = {
    'y':    60*60*24*365,
    'mo':   60*60*24*30,
    'd':    60*60*24,
    'h':    60*60,
    'm':    60,
    's':    1,
}
time_suffixes_order = 'y','mo','d','h','m','s'

def expand_time(text):
    """Convert a shorthand time notation into a value in sections"""
    #first see if it is already a plain number
    try:
        return int(text)
    except ValueError:
        pass

    for suff in time_suffixes_order:
        if text.endswith(suff):
            number_part = text[:-len(suff)]
            return int(number_part) * time_suffixes[suff]
