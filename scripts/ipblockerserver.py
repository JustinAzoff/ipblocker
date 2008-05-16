#!/usr/bin/env python

import xmlrpclib
from twisted.web import xmlrpc, server, http, resource
from twisted.internet import defer, protocol, reactor

from twisted.application import service, internet

from OpenSSL import SSL

#import datetime
#import time

class ipblocker(xmlrpc.XMLRPC):
    def __init__(self):
        pass
    
    def xmlrpc_hello(self, u, p):
        return 'hello'

class ServerContextFactory:

    def getContext(self):
        """Create an SSL context.

        This is a sample implementation that loads a certificate from a file
        called 'server.pem'."""                               
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        ctx.use_certificate_file('server.pem')
        ctx.use_privatekey_file ('server.pem')
        return ctx

def main():
    e = ipblocker()
    application = service.Application('ipblocker')
    serviceCollection = service.IServiceCollection(application)
    site = server.Site(resource.IResource(e))
    i = internet.SSLServer(7083, site, ServerContextFactory()
                       )
    i.setServiceParent(serviceCollection)
    i.startService()
    reactor.run()

if __name__ == "__main__": 
    main()