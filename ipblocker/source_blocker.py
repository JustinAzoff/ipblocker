#!/usr/bin/python

import simplejson
from ipblocker import logger
from ipblocker import util

class SourceBlocker:
    duration = 60*60*24
    must_exist_in_source = True
    blocker = None
    flag_traffic = True

    def __init__(self, model):
        self.model = model

    def get_records(self):
        raise NotImplementedError("Not implemented")

    def get_ip_from_record(self, record):
        return record['ip']

    def serialize_record(self, record):
        return simplejson.dumps(record)

    def block(self):
        all = self.get_records()
        logger.debug("Got %d ips" % len(all))
        all_ips = set(self.get_ip_from_record(r) for r in all)

        if self.must_exist_in_source:
            for b in self.model.get_all_that_should_be_blocked():
                if b.who == self.blocker and b.ip not in all_ips:
                    self.model.unblock_ip(b.ip)
                    logger.info("DB-unblocking %s" % b.ip)

        for r in all:
            msg = self.serialize_record(r)
            ip = self.get_ip_from_record(r)
            if not self.model.ok_to_block(ip):
                logger.debug("Not DB-blocking %s" % ip)
                continue
            self.model.block_ip(ip=ip, who=self.blocker, comment=msg, duration=self.duration,flag_traffic=self.flag_traffic)
            logger.debug("DB-blocking %s" % ip)

        if self.model.get_block_pending() or self.model.get_unblock_pending():
            util.wakeup_backend()
