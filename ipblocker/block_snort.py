#!/usr/bin/env python 
from snort import snortdb
from ipblocker import is_reblockable, is_fishy, ok_to_block
from ipblocker.config import config
from ipblocker.util import groupby, subnet
from operator import itemgetter

import os
import csv
import datetime

from ipblocker.source_blocker import SourceBlocker

rule_file       = config.get("snort", "rule_filename")
MINIMUM         = int(config.get("snort", "minimum"))
SUBNET_MINIMUM  = int(config.get("snort", "subnet_minimum"))
BLOCK_TIME      = config.get("snort", "block_time")

class SnortBlocker(SourceBlocker):
    blocker = "snort"
    must_exist_in_source = False
    flag_traffic = False


    def read_rules(self):
        f = csv.DictReader(open(rule_file))
        rules = []
        for x in f:
            x['minimum']        = int(x['minimum'] or  MINIMUM)
            x['subnet_minimum'] = int(x['subnet_minimum'] or  SUBNET_MINIMUM)
            x['block_time']     = x['block_time'] or  BLOCK_TIME
            rules.append(x)
        return rules

    def get_records(self):
        rules = self.read_rules()
        snort=snortdb.sdb()
        snort.setwhere(range='hour',span=1)
        snort.limit=None

        records = []
        for rule in rules:
            records.extend(self.get_records_for_rule(snort, rule))
        return records

    def get_records_for_rule(self, snort, rule):
        records = []
        alerts = snort.find(sig=rule['rule'])
        by_src = groupby(alerts, itemgetter("ip_src"))
        for ip, alerts in by_src:
            ip = str(ip)
            alerts = list(alerts)
            if is_reblockable(ip) or is_fishy(ip) or (len(alerts) >= rule['minimum'] and num_subnets(alerts) >= rule['subnet_minimum']):
                records.append(dict(ip=ip, alerts=alerts, rule=rule))
        return records

    def get_duration_from_record(self, r):
        return r['rule']['block_time']

    def serialize_record(self, r):
        alerts = r['alerts']
        txt = "%d alerts (%d subnets)\n" % (len(alerts), num_subnets(alerts))
        for a in alerts[:5]:
            txt += "%(timestamp)s %(ip_src)s:%(sport)s -> %(ip_dst)s:%(dport)s %(sig)s\n" % a
        if len(alerts) > 5:
            txt += "...\n"
            for a in alerts[-5:]:
                txt += "%(timestamp)s %(ip_src)s:%(sport)s -> %(ip_dst)s:%(dport)s %(sig)s\n" % a
        return txt

def num_subnets(alerts):
    by_dst = groupby(alerts, lambda a: subnet(a['ip_dst']))
    return len(list(by_dst))

def get_records():
    return SnortBlocker(None).get_records()

def main():
    from ipblocker import model
    b = SnortBlocker(model)
    b.block()

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", "--force",  dest="force", action="store_true", help="block without confirmation",default=False)
    (options, args) = parser.parse_args()
    main(options.force)
