#!/usr/bin/python

import simplejson
from ipblocker import logger
from ipblocker import util

class SourceBlocker:
    duration = 60*60*24
    must_exist_in_source = True
    reblockable = True
    blocker = None
    flag_traffic = True

    def __init__(self, model):
        self.model = model

    def get_records(self):
        """Return a list of block records.  This can be something like a list of IPs,
        a list of dicts, or a list of objects
        The most common case is a list of dicts where the IP address is in the 'ip' key
        """
        raise NotImplementedError("Not implemented")

    def get_ip_from_record(self, record):
        """Return just the IP address to block from a record.  If the records are a
        plain list of IP addresses, this should simply return record"""

        return record['ip']

    def serialize_record(self, record):
        """Return a textual representation from a block record.  This is what will be
        used as the comment in the database"""
        return simplejson.dumps(record)

    def get_duration_from_record(self, record):
        """Return the block duration"""
        return self.duration

    def block(self):
        """call get_records() and block each record returned.  If must_exist_in_source
        is True, unblock any addresses that were previously blocked, but are no longer
        in the source"""
        all = self.get_records()
        logger.debug("Got %d ips" % len(all))
        all_ips = set(self.get_ip_from_record(r) for r in all)

        if self.must_exist_in_source:
            for b in self.model.get_all_that_should_be_blocked():
                if b.who == self.blocker and b.ip not in all_ips:
                    self.model.unblock_ip(b.ip, forced=False)
                    logger.info("DB-unblocking %s" % b.ip)

        for r in all:
            msg = self.serialize_record(r)
            ip = self.get_ip_from_record(r)
            duration = self.get_duration_from_record(r)
            if not self.model.ok_to_block(ip):
                logger.debug("Not DB-blocking %s" % ip)
                continue
            block_record = self.model.get_blocked_ip(ip)
            if self.reblockable or not block_record:
                if block_record:
                    logger.debug("DB-re-blocking %s" % ip)
                else:
                    logger.debug("DB-blocking %s" % ip)
                self.model.block_ip(ip=ip, who=self.blocker, comment=msg, duration=duration,flag_traffic=self.flag_traffic)
                

        if self.model.get_block_pending() or self.model.get_unblock_pending():
            util.wakeup_backend()
        self.model.disconnect()
