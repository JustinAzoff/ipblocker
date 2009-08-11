"""
IPBlocker database model
========================

The main entry points in this module are the
:func:`block_ip` and
:func:`unblock_ip`
methods for adding and removing blocks, and the
:func:`get_blocked` and
:func:`get_blocked_ip`
methods for inspecting the database.

"""

import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.exceptions import SQLError
from sqlalchemy.databases.postgres import PGInet
import sqlalchemy.types as sqltypes
import ConfigParser

import datetime

from ipblocker.config import config

import psycopg2
import random



def connect():
    db_config = dict(config.items('db'))
    hosts = db_config.pop('host').split(',')
    random.shuffle(hosts)
    for host in hosts:
        try :
            return psycopg2.connect(host=host, user=db_config['user'], password=db_config['password'], database=db_config['database'])
        except Exception, e:
            pass
    raise e

#HACK
if sqlalchemy.__version__.startswith("0.5"):
    kwargs = {'autocommit': True}
else:
    kwargs = {'transactional': False}
engine = create_engine('postgres://', creator=connect,pool_recycle=60)
Session = scoped_session(sessionmaker(autoflush=True, bind=engine, **kwargs))
metadata = MetaData(bind=engine)


from sqlalchemy.orm import mapper as sqla_mapper

def session_mapper(scoped_session):
    def mapper(cls, *arg, **kw):
        if cls.__init__ is object.__init__:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
            cls.__init__ = __init__
        sqla_mapper(cls, *arg, **kw)
        cls.query = scoped_session.query_property()
    return mapper

mapper = session_mapper(Session)

try :
    from webhelpers import distance_of_time_in_words
except ImportError:
    from webhelpers.date import distance_of_time_in_words


class DontBlockException(Exception):
    def __init__(self, ip, who, comment):
        self.ip = ip
        self.who = who
        self.comment = comment
    def __str__(self):
        return "Dont Block Exception for %s (%s: %s)" % (
            self.ip, self.who, self.comment)

blocks = Table('blocks', metadata,
    Column('id',        Integer, primary_key=True),
    Column('ip',        PGInet, index=True),
    Column('who',       String(50), nullable=False),
    Column('comment',   String, nullable=False),
    Column('entered',   DateTime, default=datetime.datetime.now),
    Column('blocked',   DateTime, index=True),
    Column('unblocked', DateTime, index=True),
    Column('unblock_at', DateTime, nullable=False),
    Column('unblock_now',   Boolean, default=False,nullable=False),
    Column('flag_traffic',  Boolean, default=False,nullable=False),
)

dont_block = Table('dont_block', metadata,
    Column('id',        Integer, primary_key=True),
    Column('ip',        PGInet, index=True),
    Column('who',       String(50), nullable=False),
    Column('comment',   String, nullable=False),
    Column('entered',   DateTime, default=datetime.datetime.now),
)

fishy = Table('fishy', metadata,
    Column('ip',        PGInet, index=True, primary_key=True),
    Column('comment',   String, nullable=False),
    Column('entered',   DateTime, default=datetime.datetime.now),
)

class Fishy(object):
    def __repr__(self):
        return 'Fishy(ip="%s",comment="%s")' % (self.ip, self.comment)

class Block(object):
    """This class represents an individual blocked host"""
    def __repr__(self):
        return 'Block(ip="%s")' % self.ip

    def set_blocked(self):
        """Set this IP from pending block -> blocked
        
        >>> b.blocked is None
        True
        >>> b.set_blocked()
        >>> b.blocked is None
        False
        """
        if self.blocked:
            raise Exception("%s Already blocked!" % self.ip)
        if self.unblocked:
            raise Exception("%s Already unblocked!" % self.ip)
        self.blocked = datetime.datetime.now()
        Session.flush()

    def set_unblocked(self):
        """Set this IP from blocked -> unblocked
        
        >>> b.blocked is None
        False
        >>> b.set_unblocked()
        >>> b.blocked is None
        True
        >>> b.unblocked is None
        False
        """
        if self.unblocked: 
            raise Exception("%s Already unblocked!" % self.ip)
        #an IP can be pending blocked, but then set unblock_now
        #at this point, blocked=NULL, unblocked=NULL
        #the manager should try and unblock it(a noop) and then set
        #unblocked=now(), so blocked will still be NULL
        #if not self.blocked:
        #    raise Exception("%s not blocked yet!!" % self.ip)
        self.unblocked = datetime.datetime.now()
        Session.flush()

    def set_unblock_now(self):
        """Set this IP to be unblocked
        
        >>> b.unblock_now
        False
        >>> b.set_unblock_now()
        >>> b.unblock_now
        True
        """
        self.unblock_now = True
        Session.flush()

    def _get_unblock_at_relative(self):
        now = datetime.datetime.now()
        ago = ''
        if now > self.unblock_at:
            ago=' ago'
        return distance_of_time_in_words(now, self.unblock_at) + ago
    unblock_at_relative = property(_get_unblock_at_relative,doc="A textual representation of when this host will be unblocked")

    def _get_unblock_delta(self):
        now = datetime.datetime.now()
        diff = self.unblock_at - now
        return diff
    unblock_delta = property(_get_unblock_delta, doc="Return a datetime.timedelta object of the time until this host will be unblocked")

    def _get_unblock_pending(self):
        now = datetime.datetime.now()
        return  now > self.unblock_at
    unblock_pending = property(_get_unblock_pending, doc="Return a True if this host should be unblocked")

class DontBlock(object):
    """This class represents a host or network that should never be blocked"""
    def __repr__(self):
        return 'DontBlock(ip="%s")' % self.ip

def get_all():
    """Return a list of all the blocked and pending IPs"""
    return Block.query.filter(Block.unblocked==None).all()

def get_all_that_should_be_blocked():
    """Return a list of all the blocked and pending IPs"""
    return Block.query.filter(and_(
            Block.unblocked==None,            #hasn't been unblocked yet
            Block.unblock_now == False,       #it isn't forced unblocked
            func.now() < Block.unblock_at,    #it hasn't timed out yet
            ~exists([1],dont_block.c.ip.op(">>=")(Block.ip)),
            )).all()

def get_blocked():
    """Return a list of the currently blocked IPs"""
    return Block.query.filter(and_(Block.blocked!=None,Block.unblocked==None)).all()

def get_ip(ip):
    """Return all the block records for this ip"""
    return Block.query.filter(Block.ip==ip).all()

def get_blocked_ip(ip):
    """Return a single Blocked IP, or None if it is not currently blocked.
       Pending is considered Blocked, otherwise unblock_now won't work right"""
    return Block.query.filter(and_(Block.unblocked==None,Block.ip==ip)).first()

def get_block_pending():
    """Return a list of the IPs that are pending being blocked
       Also checks the dont_block table for any addresses that were set to be not blocked
       after an address was blocked
    """
    return Block.query.filter(and_(
        Block.blocked==None, #it's not already blocked
        Block.unblock_now==False, #it isn't forced unblocked
        func.now() < Block.unblock_at,    #it hasn't already timed out
        ~exists([1],dont_block.c.ip.op(">>=")(Block.ip)),
        )).all()

def get_unblock_pending():
    """Return a list of the IPs that are pending being un-blocked
       Also checks the dont_block table for any addresses that were set to be not blocked
       after an address was blocked
    """
    return Block.query.filter(and_(Block.unblocked==None,
            or_(
                Block.unblock_now==True,                   #force unblock
                func.now() > Block.unblock_at,             #block expired
                exists([1],dont_block.c.ip.op(">>=")(Block.ip)) #ip shouldn't be blocked
            ))).all()

def list_dont_block_records():
    """Return the list of don't block records"""
    return DontBlock.query.all()

def add_dont_block_record(ip, who, comment):
    b = DontBlock(ip=ip, who=who, comment=comment)
    Session.add(b)
    Session.flush()
    return b

def get_dont_block_record(ip):
    """Return a record from the dont_block table for this ip, if one exists"""
    r = DontBlock.query.filter(dont_block.c.ip.op(">>=")(ip)).all()
    if r:
        return r[0]

def delete_dont_block_record(id):
    dont_block.delete(dont_block.c.id==id).execute().close()

def was_force_unblocked(ip):
    """Was this IP forced to be 'unblocked now'?"""
    r = Block.query.filter(Block.ip==ip).order_by(Block.entered.desc()).first()
    if r and r.unblock_now:
        return True
    return False

def ok_to_block(ip):
    """Is this IP ok to block?"""
    r = get_dont_block_record(ip)
    if r:
        return False

    if was_force_unblocked(ip):
        return False
    return True


def block_ip(ip, who, comment, duration, flag_traffic=False, extend_only=False):
    """Block an IP address
    
    :param ip: IP Address to block
    :param who: User or system adding the block
    :param comment: Arbitrary text comment about the block
    :param duration: duration of the block in seconds
    :param flag_traffic: Should any traffic to this IP be flagged for review?
    :param extend_only: When re-blocking an already blocked host, if extend_only=True the
                        block time will not be replaced by an earlier time.
                        The extend_only option is used by the automated blockers
                        to ensure that they do not decrease a block duration.
    :rtype: The Block record


    """

    ex = get_dont_block_record(ip)
    if ex:
        raise DontBlockException(ex.ip, ex.who, ex.comment)

    now = datetime.datetime.now()
    diff = datetime.timedelta(seconds=duration)
    unblock_at = now + diff

    #if the duration is longer than 6 days, set the unblock time to exactly noon
    if duration >= 60*60*24*6:
        unblock_at = unblock_at.replace(hour=12,minute=0,second=0,microsecond=0)

    b = get_blocked_ip(ip)
    if b:
        b.flag_traffic = flag_traffic
        if b.who != who:
            b.comment += "\n" + comment
        if not ( extend_only and b.unblock_delta > diff ):
            b.unblock_at = unblock_at
        b.who = who
    else:
        b = Block(ip=ip, who=who, comment=comment, unblock_at=unblock_at, flag_traffic=flag_traffic)
    Session.add(b)
    Session.flush()
    return b

def unblock_ip(ip):
    """Un-block this IP address

    :param ip: IP Address to un-block
    """
    b = get_blocked_ip(ip)
    if b:
        b.set_unblock_now()
        return True
    else:
        return False

def is_reblockable(ip):
    """Has this ip been blocked before? if so, was it not last unblocked manually?"""
    recs = get_ip(ip)
    if not recs:
        return False
    last = recs[-1]
    #if it was forced to be unblocked, consider the last block a false positive
    if last.unblock_now:
        return False

    return True


def get_fishy_ip(ip):
    """Return a fishy record for this ip if one exists, otherwise return None"""
    r = Fishy.query.filter(fishy.c.ip==ip).first()
    return r

def is_fishy(ip):
    """Is this IP fishy?"""
    return bool(get_fishy_ip(ip))

def get_fishy():
    """List the fishy records"""
    return Fishy.query.all()

def add_fishy(ip, comment):
    """Add a fishy IP Record"""
    f = Fishy()
    f.ip = ip
    f.comment = comment
    Session.add(f)
    Session.flush()

def del_fishy(ip):
    """Remove a fishy IP record"""
    fishy.delete(fishy.c.ip==ip).execute().close()

mapper(Block, blocks)
mapper(DontBlock, dont_block)
mapper(Fishy, fishy)

#CREATE INDEX idx_blocked_null   ON blocks (blocked)   WHERE blocked IS NULL;
#CREATE INDEX idx_unblocked_null ON blocks (unblocked) WHERE unblocked IS NOT NULL;

__all__ = '''
    Block DontBlockException
    get_all get_all_that_should_be_blocked get_blocked get_ip
    get_blocked_ip get_block_pending get_unblock_pending list_dont_block_records
    add_dont_block_record get_dont_block_record delete_dont_block_record
    ok_to_block block_ip unblock_ip is_reblockable
    get_fishy_ip is_fishy get_fishy add_fishy del_fishy'''.split()

