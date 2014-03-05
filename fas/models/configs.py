# -*- coding: utf-8 -*-
from . import Base

from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    UnicodeText,
    DateTime,
    Boolean,
    ForeignKey,
    func
    )


class Plugins(Base):
    __tablename__ = 'plugins'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    comment = Column(UnicodeText(), nullable=True)
    enabled = Column(Boolean, nullable=False, default=False)


class AccountPermissions(Base):
    __tablename__ = 'account_permissions'
    id = Column(Integer, primary_key=True)
    people = Column(Integer, ForeignKey('people.id'), nullable=False)
    token = Column(UnicodeText(), unique=True, nullable=False)
    application = Column(UnicodeText(), nullable=False)
    permissions = Column(Integer, nullable=False)
    granted_timestamp = Column(
        DateTime, nullable=False,
        default=func.current_timestamp())
