from ipblocker import util
import IPy
def test_subnet():
    tests = [
        ('1.2.3.4', 3),
        ('1.2.3.5', 3),
        ('1.1.1.1', 1),
    ]
    for ip, sn in tests:
        yield subnet_case, IPy.IP(ip), sn

def subnet_case(ip, sn):
    assert util.subnet(ip) == sn


def fix(data):
    for x in data:
        x['srcip'] = IPy.IP(x['srcip'])
        x['dstip'] = IPy.IP(x['dstip'])
    return data

def test_ip_summary_simple():
    data = fix([
        dict(srcip='1.2.3.4',dstip='1.1.1.1'),
        dict(srcip='1.2.3.4',dstip='1.1.1.2'),
        dict(srcip='1.2.3.4',dstip='1.1.1.3'),
        dict(srcip='1.2.3.4',dstip='1.1.2.2'),
        dict(srcip='1.2.3.4',dstip='1.1.3.3'),
    ])
    

    summary = util.ip_summary(data)
    assert len(summary)==1
    assert IPy.IP("1.2.3.4") in summary
    info = summary[IPy.IP("1.2.3.4")]
    assert info['num_flows'] == 5
    assert info['num_subnets'] == 3
    assert info['stop_flows'] == []

def test_expand_time():
    data = [
        ('10',      10),
        ('10s',     10),
        ('7m',      7*60),
        ('14m',     14*60),
        ('4h',      4*60*60),
        ('22h',     22*60*60),
        ('3d',      3*60*60*24),
        ('3mo',     3*60*60*24*30),
        ('2y',      2*60*60*24*365),
    ]

    for text, number in data:
        yield expand_time_case, text, number

def expand_time_case(text, number):
    assert util.expand_time(text) == number 
