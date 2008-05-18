from ipblocker import model
import time

IP = '1.2.3.4'

def test_nothing_pending():
    pending = model.Block.get_block_pending()
    assert len(pending)==0

def test_block_ip():
    block = model.block_ip(IP, 'justin', 'just testing', 3)
    pending = model.Block.get_block_pending()
    assert len(pending)==1
    assert pending[0].ip == IP

def test_set_blocked():
    blocked = model.Block.get_blocked()
    assert len(blocked)==0

    pending = model.Block.get_block_pending()
    assert len(pending)==1

    b = pending[0]
    assert b.ip == IP
    b.set_blocked()

    blocked = model.Block.get_blocked()
    assert len(blocked)==1
    b = blocked[0]
    assert b.ip == IP

def test_get_blocked_ip():
    b = model.Block.get_blocked_ip(IP)
    assert b.ip == IP

def test_set_blocked_again():
    blocked = model.Block.get_blocked()
    b = blocked[0]
    orig = b.unblock_at

    block = model.block_ip(IP, 'justin', 'just testing', 3)
    assert block is b
    print
    print 'original:', orig
    print 'new     :', block.unblock_at
    assert block.unblock_at != orig

def test_unblock_pending():
    pending = model.Block.get_unblock_pending()
    assert len(pending)==0
    time.sleep(4)
    pending = model.Block.get_unblock_pending()
    assert len(pending)==1
    b = pending[0]
    assert b.ip == IP

def test_set_unblocked():
    pending = model.Block.get_unblock_pending()
    assert len(pending)==1
    b = pending[0]
    assert b.ip == IP
    b.set_unblocked()

def test_is_unblocked():
    blocked = model.Block.get_blocked()
    assert len(blocked)==0

def test_cleanup():
    B = model.Block 
    for x in B.query.filter(B.ip==IP).all():
        model.Session.delete(x)
    model.Session.flush()
