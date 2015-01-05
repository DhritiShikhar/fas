
from . import Base, LicenseAgreementStatus

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
from sqlalchemy.orm import relation


class LicenseAgreement(Base):
    """ Mapper class to SQL table LicenseAgreement. """
    __tablename__ = 'license_agreement'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    status = Column(Integer, default=LicenseAgreementStatus.DISABLED)
    content = Column(UnicodeText, nullable=False)
    comment = Column(UnicodeText, nullable=True)
    enabled_at_signup = Column(Boolean, default=False)
    creation_timestamp = Column(
        DateTime,
        nullable=False,
        default=func.current_timestamp()
    )
    update_timestamp = Column(
        DateTime,
        nullable=False,
        default=func.current_timestamp()
    )

    groups = relation(
        'Groups',
        foreign_keys='Groups.license_sign_up',
        primaryjoin='and_(LicenseAgreement.id==Groups.license_sign_up)',
        order_by='Groups.name'
    )


class SignedLicenseAgreement(Base):
    """ Mapper class to SQL table SignedLicenseAgreement. """
    __tablename__ = 'signed_license_agreement'
    id = Column(Integer, primary_key=True)
    license = Column(
        Integer,
        ForeignKey('license_agreement.id')
        )
    people = Column(Integer, ForeignKey('people.id'))
    signed = Column(Boolean, nullable=False)

    licenses = relation(
        'LicenseAgreement',
        order_by='LicenseAgreement.id'
    )
