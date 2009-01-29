try :
    from amqpevent import Events
except ImportError
    Events = None

e = None

def notify_block(b):
    if not Events:
        return

    global e
    try :
        if e is None:
            e=Events('notify')
        e.add_event("ipb: %s - %s" % ( b.ip, b.who))
    except:
        pass
