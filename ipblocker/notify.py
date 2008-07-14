from amqpevent import Events
e=Events('notify')

def notify_block(b):
    e.add_event("ipb: %s\n%s" % ( b.ip, b.comment))
