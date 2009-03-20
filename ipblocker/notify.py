try :
    from kestrel import Client
except ImportError:
    Client = None

def notify_block(b):
    if not Client:
        return

    try :
        c=Client(['test:22133','localhost:22133'])
        c.set("notify", "ipb: %s - %s" % ( b.ip, b.who))
        c.disconnect_all()
    except:
        pass
