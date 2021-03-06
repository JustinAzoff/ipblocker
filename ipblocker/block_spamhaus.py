#!/usr/bin/env python
import httplib2
import os

from ipblocker import model, logger
from ipblocker.config import config
from ipblocker import util
from ipblocker.source_blocker import SourceBlocker

class SHBlocker(SourceBlocker):
    blocker = 'spamhaus'
    duration = 60*60*24*30
    must_exist_in_source = True
    flag_traffic = False

    def get_records(self):
        h = httplib2.Http(os.path.expanduser("~/.httplib2_cache"))
        logger.debug("Fetching IP list from spamhaus")
        resp, content = h.request("http://www.spamhaus.org/drop/drop.lasso")
        records = []
        for line in content.splitlines():
            ip, comment = line.split(";")
            ip = ip.strip()
            comment = comment.strip()
            if ip:
                records.append({'ip': ip, 'comment': comment})
        return records
        
    def serialize_record(self, record):
        return "on the spamhaus drop list - %s" % record['comment']

def get_records():
    return SHBlocker(None).get_records()

def main():
    b = SHBlocker(model)
    b.block()

if __name__ == "__main__":
    main()
