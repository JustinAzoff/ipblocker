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


class Block(object):

    def __repr__(self):
        return 'Block(ip="%s")' % self.ip

    @classmethod
    def get_blocked(cls):
        return cls.query.filter(and_(cls.blocked!=None,cls.unblocked==None)).all()

    @classmethod
    def get_blocked_ip(cls,ip):
        return cls.query.filter(and_(cls.blocked!=None,cls.unblocked==None,cls.ip==ip)).first()

    @classmethod
    def get_block_pending(cls):
        return cls.query.filter(cls.blocked==None).all()

    @classmethod
    def get_unblock_pending(cls):
        return cls.query.filter(and_(
                or_(cls.unblock_now==True, func.now() > cls.unblock_at),
                cls.unblocked==None)).all()

    def set_blocked(self):
        self.blocked = datetime.datetime.now()
        Session.flush()

    def set_unblocked(self):
        self.unblocked = datetime.datetime.now()
        Session.flush()

    def set_unblock_now(self):
        self.unblock_now = True
        Session.flush()
    

def block_ip(ip, who, comment, duration):
    now = datetime.datetime.now()
    diff = datetime.timedelta(seconds=duration)
    unblock_at = now + diff

    b = Block.get_blocked_ip(ip)
    if b:
        b.who = who
        b.comment = comment
        b.unblock_at = unblock_at
    else:
        b = Block(ip=ip, who=who, comment=comment, unblock_at=unblock_at)
    Session.flush()
    return b

def get_blocked_ip(ip):
    b = Block.get_blocked_ip(ip)
    return b

def unblock_ip(ip):
    b = get_blocked_ip(ip)
    if b:
        b.set_unblock_now()
        return True
    else:
        return False

mapper(Block, blocks)

#CREATE INDEX idx_blocked_null   ON blocks (blocked)   WHERE blocked IS NULL;
#CREATE INDEX idx_unblocked_null ON blocks (unblocked) WHERE unblocked IS NOT NULL;

