#!/usr/bin/python

from ipblocker import logger
import time
from ipblocker.notify import notify_block

try :
    import mymemcache
except ImportError:
    mymemcache = None

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
            to_unblock[b.ip] = b
            if b.ip not in current:
                logger.warning("already unblocked %s, unblocking anyway" % b.ip)
            else:
                logger.info("unblocking %s (%s)" % (b.ip, b.who))

        if not to_unblock:
            return

        c.nullroute_remove_many(to_unblock.keys())
        current = set(c.nullroute_list())

        for b in to_unblock.values():
            if b.ip not in current:
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
            to_block[b.ip] = b
            if b.ip not in current:
                logger.info("blocking %s (%s)" % (b.ip, b.who))
                notify_block(b)
            else:
                logger.warning("already blocked %s, blocking anyway" % b.ip)

        if not to_block:
            return

        c.nullroute_add_many(to_block.keys())
        current = set(c.nullroute_list())

        for b in to_block.values():
            if b.ip in current:
                b.set_blocked()
            else:
                logger.error("error blocking %s" % b.ip)


    def manage(self):
        self.model.Session.clear()
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

        if mymemcache:
            mc = mymemcache.Client(timeout=60*60)
            mc['ipblocker:last_manager_runtime'] = time.ctime()
        self.model.engine.dispose()
