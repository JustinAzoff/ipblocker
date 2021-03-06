#!/usr/bin/python

from ipblocker import logger, config, util
import time
from ipblocker.notify import notify_block

from IPy import IP

try :
    import memcache
except ImportError:
    memcache = None

class Manager:
    def __init__(self, ip, model_class, cisco_class):
        self.ip = ip
        self.connection = None
        self.cisco = cisco_class
        self.model = model_class

    def get_connection(self):
        if self.connection:
            return self.connection
        
        logger.debug("Logging into router")
        conn = self.cisco.login(self.ip)
        if not conn:
            logger.error("Unable to login to router")
            raise Exception("Unable to login to router")
        logger.debug("Done logging into router")
        self.connection = conn
        return conn

    def unblock(self):
        unblock_pending = self.model.get_unblock_pending()
        if not unblock_pending:
            return

        c = self.get_connection()
        current = set(c.nullroute_list())
        to_unblock = {}
        for b in unblock_pending:
            if IP(b.ip) not in current:
                logger.warning("already unblocked %s" % b.ip)
            else:
                logger.info("unblocking %s (%s)" % (b.ip, b.who))
                to_unblock[IP(b.ip)] = b

        if to_unblock:
            for batch in util.window(to_unblock.keys(), 250):
                c.nullroute_remove_many(batch)
            current = set(c.nullroute_list())

        for b in unblock_pending:
            if IP(b.ip) not in current:
                b.set_unblocked()
            else:
                logger.error("error unblocking %s" % b.ip)

        out = c.write_mem()
        out = ' '.join(out)
        logger.info("write mem: %s" % out)

    def block(self):
        block_pending = self.model.get_block_pending()
        if not block_pending:
            return
        c = self.get_connection()
        current = set(c.nullroute_list())
        to_block = {}
        for b in block_pending:
            if IP(b.ip) in current:
                logger.warning("already blocked %s" % b.ip)
            else:
                logger.info("blocking %s (%s)" % (b.ip, b.who))
                to_block[IP(b.ip)] = b
                notify_block(b)

        if to_block:
            for batch in util.window(to_block.keys(), 250):
                c.nullroute_add_many(batch)
            current = set(c.nullroute_list())

        for b in block_pending:
            if IP(b.ip) in current:
                b.set_blocked()
            else:
                logger.error("error blocking %s" % b.ip)


    def manage(self):
        self.model.Session.expunge_all()
        try:
            self.unblock()
        except Exception, e:
            logger.error("error unblocking %s" % e)

        try:
            self.block()
        except Exception, e:
            logger.error("error blocking %s" % e)

        if self.connection:
            logger.debug("Logging out of router")
            self.connection.logout()

        host = config.get("blocking","memcache_host")
        if memcache and host:
            mc = memcache.Client([host])
            mc.set("ipblocker:last_manager_runtime", time.ctime())
        self.model.disconnect()
