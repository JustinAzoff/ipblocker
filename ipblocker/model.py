from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.exceptions import SQLError
from sqlalchemy import *
import sqlalchemy.types as sqltypes
import ConfigParser

import datetime

c = ConfigParser.ConfigParser()
c.read(['/etc/ipblocker/db.cfg','db.cfg'])
engine = create_engine(c.get('db','uri'))
Session = scoped_session(sessionmaker(autoflush=True, transactional=False, bind=engine))
metadata = MetaData(bind=engine)
mapper = Session.mapper

class PGMac(sqltypes.TypeEngine):
    def get_col_spec(self):
        return "MACADDR"

class PGInet(sqltypes.TypeEngine):
    def get_col_spec(self):
        return "INET"

class DontBlockException(Exception):
    pass

blocks = Table('blocks', metadata,
    Column('id',        Integer, primary_key=True),
    Column('ip',        PGInet, index=True),
    Column('who',       String(50), nullable=False),
    Column('comment',   String, nullable=False),
    Column('entered',   DateTime, default=datetime.datetime.now),
    Column('blocked',   DateTime, index=True),
    Column('unblocked', DateTime, index=True),
    Column('unblock_at', DateTime, nullable=False),
    Column('unblock_now',   Boolean, default=False,nullable=False)
)

dont_block = Table('dont_block', metadata,
    Column('id',        Integer, primary_key=True),
    Column('ip',        PGInet, index=True),
    Column('who',       String(50), nullable=False),
    Column('comment',   String, nullable=False),
)

#and IP can be pending blocked, but then set unblock_now
#at this point, blocked=NULL, unblocked=NULL
#the manager should try and unblock it(a noop) and then set
#unblocked=now(), so blocked will still be NULL
class Block(object):
    def __repr__(self):
        return 'Block(ip="%s")' % self.ip

    def set_blocked(self):
        """Set this IP from pending block -> blocked"""
        self.blocked = datetime.datetime.now()
        Session.flush()

    def set_unblocked(self):
        """Set this IP from blocked -> unblocked"""
        self.unblocked = datetime.datetime.now()
        Session.flush()

    def set_unblock_now(self):
        """Set this IP to be unblocked"""
        self.unblock_now = True
        Session.flush()

def get_all():
    """Return a list of all the blocked and pending IPS"""
    return Block.query.filter(Block.unblocked==None).all()

def get_blocked():
    """Return a list of the currently blocked IPS"""
    return Block.query.filter(and_(Block.blocked!=None,Block.unblocked==None)).all()

def get_blocked_ip(ip):
    """Return a single Blocked IP, or None if it is not currently blocked
       Pending is considered Blocked, otherwise unblock_now won't work right"""
    return Block.query.filter(and_(Block.unblocked==None,Block.ip==ip)).first()

def get_block_pending():
    """Return a list of the IPS that are pending being blocked"""
    return Block.query.filter(and_(Block.blocked==None,Block.unblock_now==False)).all()

def get_unblock_pending():
    """Return a list of the IPS that are pending being un-blocked"""
    return Block.query.filter(and_(
            or_(Block.unblock_now==True, func.now() > Block.unblock_at),
            Block.unblocked==None)).all()
    
def get_dont_block_record(ip):
    """Return a record from the dont_block table for this ip, if one exists"""
    r = dont_block.select(dont_block.c.ip.op(">>=")(ip)).execute().fetchall()
    if r:
        return r[0]

def block_ip(ip, who, comment, duration):
    """Block this IP address"""

    ex = get_dont_block_record(ip)
    if ex:
        raise DontBlockException("%s:%s" %(ex.who, ex.comment))

    now = datetime.datetime.now()
    diff = datetime.timedelta(seconds=duration)
    unblock_at = now + diff

    b = get_blocked_ip(ip)
    if b:
        b.who = who
        b.comment = comment
        b.unblock_at = unblock_at
    else:
        b = Block(ip=ip, who=who, comment=comment, unblock_at=unblock_at)
    Session.flush()
    return b

def unblock_ip(ip):
    """Un-block this IP address"""
    b = get_blocked_ip(ip)
    if b:
        b.set_unblock_now()
        return True
    else:
        return False

mapper(Block, blocks)

#CREATE INDEX idx_blocked_null   ON blocks (blocked)   WHERE blocked IS NULL;
#CREATE INDEX idx_unblocked_null ON blocks (unblocked) WHERE unblocked IS NOT NULL;

__all__ = '''
    Block
    get_blocked get_blocked_ip get_block_pending get_unblock_pending
    get_dont_block_record
    block_ip unblock_ip'''.split()
