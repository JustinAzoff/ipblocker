#!/usr/bin/python

from ipblocker import logger

from IPy import IP

try :
    import memcache
except ImportError:
    memcache = None

class Auditor:
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

    def audit(self):
        c = self.get_connection()

        not_blocked = []
        blocked = []

        expected = self.model.get_all_that_should_be_blocked()
        expected_ips = [IP(x.ip) for x in expected]

        current = c.nullroute_list()
        current_set = set(current)

        for x in expected:
            if IP(x.ip) not in current_set:
                not_blocked.append(x)
        for x in current:
            if x not in expected_ips:
                blocked.append(x)

        c.logout()
        self.model.disconnect()
        return not_blocked, blocked
