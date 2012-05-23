#!/usr/bin/env python
from cif import Client

from ipblocker import model, logger
from ipblocker.config import config
from ipblocker import util
from ipblocker.source_blocker import SourceBlocker

class CifBlocker(SourceBlocker):
    blocker = 'cif'
    duration = 60*60*24*30
    must_exist_in_source = True
    flag_traffic = True

    def get_records(self):
        host = config.get("cif","host")
        apikey = config.get("cif","apikey")

        records = []
        c = Client(host, apikey, no_verify_tls=True)
        for feed in 'infrastructure/malware', 'infrastructure/botnet', 'infrastructure/scan':
            records.extend(c.GET(feed, severity="medium", confidence="85", simple=True)['feed']['entry'])
        return records

    def get_flag_from_record(self, record):
        return record.get("impact") != 'scanner'

    def get_ip_from_record(self, record):
        return record['address']
       
    def serialize_record(self, record): 
        keys = "portlist", "protocol", "description", "alternativeid"
        out = ""
        for k in keys:
            out += "%s: %s\n" % (k, record.get(k,''))
        return out

def get_records():
    return CifBlocker(None).get_records()

def main():
    b = CifBlocker(model)
    b.block()

if __name__ == "__main__":
    main()
