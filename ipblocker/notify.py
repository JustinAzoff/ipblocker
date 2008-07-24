from amqpevent import Events
e = None

def notify_block(b):
    global e
    try :
        if e is None:
            e=Events('notify')
        e.add_event("ipb: %s - %s" % ( b.ip, b.who))
    except:
        pass
