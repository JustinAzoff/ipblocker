from ipblocker import *
import time

IP = '4.4.4.4'

def test_nothing_pending():
    pending = model.get_block_pending()
    assert len(pending)==0

def test_block_ip():
    block = block_ip(IP, 'justin', 'just testing', 3)
    pending = model.get_block_pending()
    assert len(pending)==1
    assert pending[0].ip == IP

def test_set_blocked():
    blocked = model.get_blocked()
    assert len(blocked)==0

    pending = model.get_block_pending()
    assert len(pending)==1

    b = pending[0]
    assert b.ip == IP
    b.set_blocked()

    blocked = model.get_blocked()
    assert len(blocked)==1
    b = blocked[0]
    assert b.ip == IP

def test_get_blocked_ip():
    b = get_blocked_ip(IP)
    assert b.ip == IP

def test_set_blocked_again():
    blocked = model.get_blocked()
    b = blocked[0]
    orig = b.unblock_at

    block = block_ip(IP, 'justin', 'just testing', 3)
    assert block is b
    print
    print 'original:', orig
    print 'new     :', block.unblock_at
    assert block.unblock_at != orig

def test_set_blocked_again_shorter_time_a():
    block = block_ip(IP, 'justin', 'just testing', 60)
    blocked = model.get_blocked()
    b = blocked[0]
    orig = b.unblock_at
    block = block_ip(IP, 'justin', 'just testing', 10)
    assert block is b
    assert block.unblock_at != orig

def test_set_blocked_again_shorter_time_b():
    block = block_ip(IP, 'justin', 'just testing', 60)
    blocked = model.get_blocked()
    b = blocked[0]
    orig = b.unblock_at
    block = block_ip(IP, 'justin', 'just testing', 10, extend_only=True)
    assert block is b
    assert block.unblock_at == orig

def test_unblock_pending():
    #force this to be pending in 4 seconds
    block = block_ip(IP, 'justin', 'just testing', 4)
    pending = model.get_unblock_pending()
    print pending
    assert len(pending)==0
    time.sleep(4)
    pending = model.get_unblock_pending()
    assert len(pending)==1
    b = pending[0]
    assert b.ip == IP

def test_set_unblocked():
    pending = model.get_unblock_pending()
    assert len(pending)==1
    b = pending[0]
    assert b.ip == IP
    b.set_unblocked()

def test_is_unblocked():
    blocked = model.get_blocked()
    assert len(blocked)==0

def test_unblock_now():
    block = block_ip(IP, 'justin', 'just testing', 10)
    block.set_blocked()

    assert model.was_force_unblocked(IP) == False

    pending = model.get_unblock_pending()
    assert len(pending)==0
    block.set_unblock_now()
    pending = model.get_unblock_pending()
    assert len(pending)==1

    assert model.was_force_unblocked(IP) == True

def test_dont_block():
    b = model.get_dont_block_record(IP)
    assert b is None
    model.add_dont_block_record(IP, 'justin','testing')
    b = model.get_dont_block_record(IP)
    assert b.ip == IP
    try:
        block = block_ip(IP, 'justin', 'just testing', 3)
        raise Exception('Did not prevent %s from being blocked' % IP)
    except model.DontBlockException:
        pass
    model.delete_dont_block_record(b.id)
    b = model.get_dont_block_record(IP)
    assert b is None


def test_cleanup():
    B = model.Block 
    for x in B.query.filter(B.ip==IP).all():
        model.Session.delete(x)
    model.Session.flush()


def test_fishy():
    assert is_fishy(IP) == False

    add_fishy(IP, 'test')
    assert is_fishy(IP) == True

    f = get_fishy_ip(IP)
    assert f.ip == IP
    assert f.comment == 'test'

    del_fishy(IP)
    assert is_fishy(IP) == False
