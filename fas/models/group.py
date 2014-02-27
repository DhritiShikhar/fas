from . import Base

from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    UnicodeText,
    DateTime,
    Sequence,
    Boolean,
    ForeignKey,
    Index
    )
from sqlalchemy.orm import relation
import datetime

class GroupType(Base):
    __tablename__ = 'group_type'
    id = Column(Integer, unique=True, primary_key=True)
    name = Column(UnicodeText(), unique=True, nullable=False)
    comment = Column(UnicodeText(), nullable=True)

    __table_args__ = (
        Index('group_type_name_idx', name),
    )

    @classmethod
    def by_id(cls, session, id):
        """ Retrieve a specific GroupType by its id. """
        query = session.query(cls).filter(id=id)
        return query.first()


class Groups(Base):
    __tablename__ = 'group'
    id = Column(Integer, Sequence('group_seq', start=20000), primary_key=True)
    name = Column(Unicode(40), unique=True, nullable=False)
    display_name = Column(UnicodeText(), nullable=True)
    url = Column(UnicodeText(), nullable=True)
    mailing_list = Column(UnicodeText(), nullable=True)
    mailing_list_url = Column(UnicodeText(), nullable=True)
    irc_channel = Column(UnicodeText(), nullable=True)
    irc_network = Column(UnicodeText(), nullable=True)
    owner_id = Column(Integer, ForeignKey('people.id'), nullable=False)
    group_type_id = Column(Integer, ForeignKey('group_type.id'), default=0)
    parent_group_id = Column(Integer, ForeignKey('group.id'), default=0)
    self_removal = Column(Boolean, default=True)
    need_approval = Column(Boolean, default=False)
    invite_only = Column(Boolean, default=False)
    join_msg = Column(UnicodeText(), nullable=True)
    apply_rules = Column(UnicodeText(), nullable=True)
    created = Column(DateTime, default=datetime.datetime.utcnow())

    owner = relation("people")
    group_type = relation("group_type")
    parent_group = relation("group")

    __table_args__ = (
        Index('group_name_idx', name),
    )

    @classmethod
    def by_id(cls, session, id):
        """ Retrieve a specific Group by its id. """
        query = session.query(cls).filter(id==id)
        return query.first()

    @classmethod
    def by_name(cls, session, name):
        """ Retrieve a specific Group by its id. """
        query = session.query(cls).filter(name==name)
        return query.first()

