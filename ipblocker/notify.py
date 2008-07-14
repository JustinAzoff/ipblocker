from amqpevent import Events
e = None

def notify_block(b):
    global e
    try :
        if e is None:
            e=Events('notify')
        e.add_event("ipb: %s\n%s" % ( b.ip, b.comment))
    except:
        pass
