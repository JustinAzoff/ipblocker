from ipblocker import config
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
    import tcpsleep
    db_config = dict(config.items('db'))
    host = db_config.pop('host').split(',')[0]
    return tcpsleep.client.wakeup(host=host, port=11112)

