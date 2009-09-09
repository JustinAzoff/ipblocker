from ipblocker.source_blocker import SourceBlocker

class Thing:
    def __init__(self, **kwargs):
        for a,b in kwargs.items():
            setattr(self, a,b)


class fake_model:
    def __init__(self):
        self.blocked = []
        self.block_pending = []
        self.unblock_pending = []

    def get_all_that_should_be_blocked(self):
        return self.blocked

    def get_block_pending(self):
        return self.block_pending
    def get_unblock_pending(self):
        return self.unblock_pending

    def ok_to_block(self, ip):
        return True
    def block_ip(self, ip, who, comment, duration,flag_traffic):
        self.block_pending.append(ip)
    def unblock_ip(self, ip):
        self.unblock_pending.append(ip)

class a_blocker(SourceBlocker):
    blocker = 'whatever'
    def get_records(self):
        return []

def test_do_nothing():
    m = fake_model()
    b = a_blocker(m)
    b.block()
    assert m.get_block_pending() == []
    assert m.get_unblock_pending() == []

class b_blocker(SourceBlocker):
    def get_records(self):
        return [{'ip': '4.4.4.4'}]

def test_block_something():
    m = fake_model()
    b = b_blocker(m)
    b.block()
    assert m.get_block_pending() == ['4.4.4.4']
    assert m.get_unblock_pending() == []

def test_unblock_something():
    m = fake_model()
    m.blocked.append(Thing(ip='4.4.4.4',who='whatever'))
    b = a_blocker(m)
    b.block()
    assert m.get_block_pending() == []
    assert m.get_unblock_pending() == ['4.4.4.4']
