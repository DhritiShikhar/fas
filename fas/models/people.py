# -*- coding: utf-8 -*-
#
# Copyright © 2014-2015 Xavier Lamien.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
__author__ = 'Xavier Lamien <laxathom@fedoraproject.org>'

from . import (
    Base,
    AccountStatus
    )

from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    UnicodeText,
    DateTime,
    Sequence,
    Boolean,
    Numeric,
    Index,
    ForeignKey,
    func
    )

from sqlalchemy.orm import (
    relation,
    relationship,
    backref
    )

from fas.models import AccountPermissionType as perm

from fas.util import format_datetime, utc_iso_format

import datetime


class People(Base):
    """ Class mapping SQL table People."""
    __tablename__ = 'people'
    id = Column(
        Integer,
        Sequence('people_seq', start='10000'),
        primary_key=True)
    username = Column(Unicode(255), unique=True, nullable=False)
    password = Column(UnicodeText(), nullable=False)
    fullname = Column(UnicodeText(), nullable=False)
    ircnick = Column(UnicodeText(), unique=True, nullable=True)
    avatar = Column(UnicodeText(), nullable=True)
    avatar_id = Column(Unicode, nullable=True)
    introduction = Column(UnicodeText(), nullable=True)
    postal_address = Column(UnicodeText(), nullable=True)
    country_code = Column(Unicode(2), nullable=True)
    locale = Column(UnicodeText, default=u'en_US')
    birthday = Column(Integer(), nullable=True)
    birthday_month = Column(UnicodeText(), nullable=True)
    telephone = Column(UnicodeText(), nullable=True)
    facsimile = Column(UnicodeText(), nullable=True)
    affiliation = Column(UnicodeText(), nullable=True)
    bio = Column(UnicodeText(), nullable=True)
    timezone = Column(UnicodeText(), default=u'UTC')
    gpg_id = Column(UnicodeText(), nullable=True)
    gpg_fingerprint = Column(UnicodeText(), nullable=True)
    ssh_key = Column(UnicodeText(), nullable=True)
    email = Column(UnicodeText(), unique=True, nullable=False)
    recovery_email = Column(UnicodeText(), unique=True, nullable=True)
    bugzilla_email = Column(UnicodeText(), unique=True, nullable=True)
    email_token = Column(UnicodeText(), unique=True, nullable=True)
    unverified_email = Column(UnicodeText(), nullable=True)
    security_question = Column(UnicodeText(), default=u'-')
    security_answer = Column(UnicodeText(), default=u'-')
    login_attempt = Column(Integer(), nullable=True)
    password_token = Column(UnicodeText(), nullable=True)
    old_password = Column(UnicodeText(), nullable=True)
    certificate_serial = Column(Integer, default=1)
    status = Column(Integer, default=AccountStatus.PENDING)
    status_change = Column(DateTime, default=datetime.datetime.utcnow)
    privacy = Column(Boolean, default=False)
    email_alias = Column(Boolean, default=True)
    blog_rss = Column(UnicodeText(), nullable=True)
    latitude = Column(Numeric, nullable=True)
    longitude = Column(Numeric, nullable=True)
    fas_token = Column(UnicodeText(), nullable=True)
    github_token = Column(UnicodeText(), nullable=True)
    twitter_token = Column(UnicodeText(), nullable=True)
    last_logged = Column(DateTime, default=datetime.datetime.utcnow)
    date_created = Column(
        DateTime, nullable=False,
        default=func.current_timestamp()
    )
    date_updated = Column(
        DateTime, nullable=False,
        default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    groups = relation(
        'Groups',
        order_by='Groups.id'
    )
    #account_status = relation(
        #'AccountStatus',
        #foreign_keys='People.status',
        #uselist=False
    #)
    group_membership = relationship(
        'GroupMembership',
        primaryjoin='and_(GroupMembership.people_id==People.id)',
        backref=backref('people', lazy="joined")
        )
    group_sponsors = relation(
        'GroupMembership',
        foreign_keys='GroupMembership.sponsor',
        uselist=False
    )
    licenses = relation(
        'SignedLicenseAgreement',
        order_by='SignedLicenseAgreement.id'
    )
    activities_log = relation(
        'PeopleAccountActivitiesLog',
        order_by='PeopleAccountActivitiesLog.timestamp'
    )
    account_permissions = relation(
        'AccountPermissions',
        primaryjoin='and_(AccountPermissions.people==People.id)',
        order_by='AccountPermissions.id'
    )

    __table_args__ = (
        Index('people_username_idx', username),
    )

    def get_status(self):
        """ Retrieve person status definition and return it. """
        return AccountStatus[self.status]

    def get_created_date(self, request):
        """ Return activity date in a translated human readable format. """
        return format_datetime(request.locale_name, self.date_created)

    def to_json(self, permissions):
        """ Return a json/dict representation of this user.

        Use the `filter_private` argument to retrieve all the information about
        the user or just the public information.
        By default only the public information are returned.

        :param permissions: permission level to return related infos
        :type permissions: `fas.models.AccountPermissionLevel`
        :return: json/dict format of user data
        :rtype: dict
        """
        info = {}
        if permissions >= perm.CAN_READ_PUBLIC_INFO:
            # Standard public info
            info = {
                'id': self.id,
                'username': self.username,
                'fullname': self.fullname,
                'ircnick': self.ircnick,
                'avatar': self.avatar,
                'email': self.email,
                'creationDate': utc_iso_format(self.date_created),
                'status': self.status,
                'timezone': self.timezone
            }

        if permissions >= perm.CAN_READ_PEOPLE_FULL_INFO:
            info['countryCode'] = self.country_code
            info['locale'] = self.locale
            info['bugzillaEmail'] = self.bugzilla_email or self.email
            info['gpgId'] = self.gpg_id
            info['blogrss'] = self.blog_rss
            info['bio'] = self.bio

            info['membership'] = []
            if self.group_membership > 0:
                for groups in self.group_membership:
                    info['membership'].append(
                        {
                            'groupId': groups.group_id,
                            'groupName': groups.group.name,
                            'groupType': groups.group.group_type,
                            'groupSponsorId': groups.sponsor,
                            'groupRole': groups.role,
                            'status': groups.status,
                            'groupStatus': groups.group.status
                        }
                    )

            # Infos that people set as private
            if not self.privacy:
                info['emailAlias'] = self.email_alias
                info['postalAddress'] = self.postal_address
                info['telephone'] = self.telephone
                info['facsimile'] = self.facsimile
                info['affiliation'] = self.affiliation
                info['certificateSerial'] = self.certificate_serial
                info['sshKey'] = self.ssh_key
                info['latitude'] = int(self.latitude or 0.0)
                info['longitude'] = int(self.longitude or 0.0)
                info['lastLogged'] = self.last_logged.strftime(
                    '%Y-%m-%d %H:%M')

                info['connectedApplications'] = {
                    # 'fas': self.fas_token,
                    'github': 'connected' if self.github_token else 'inactivate',
                    'twitter': 'connected' if self.twitter_token else 'inactivate'
                }

                if self.account_permissions:
                    info['accountAccess'] = []
                    for perms in self.account_permissions:
                        info['accountAccess'].append(
                            {
                                'application': perms.application,
                                'permissions': perms.permissions,
                                'grantedOn':
                                    perms.granted_timestamp.strftime(
                                        '%Y-%m-%d')
                            }
                        )

                if self.activities_log:
                    info['accountActivities'] = []
                    for log in self.activities_log:
                        info['accountActivities'].append(
                            {
                                'location': log.location + ' (%s)' % log.remote_ip,
                                'accessFrom': log.access_from,
                                'datetime': log.timestamp.strftime(
                                    '%Y-%m-%d %H:%M')
                            }
                        )
            else:
                info['privacy'] = self.privacy

        return info


class PeopleAccountActivitiesLog(Base):
    __tablename__ = 'people_activity_log'
    id = Column(Integer, primary_key=True)
    people = Column(Integer, ForeignKey('people.id'), nullable=False)
    location = Column(UnicodeText(), nullable=False)
    remote_ip = Column(Unicode, nullable=False)
    access_from = Column(UnicodeText(), nullable=False)
    event = Column(Integer, nullable=False)
    event_msg = Column(UnicodeText(), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow())

    person = relation('People', uselist=False)

    __table_args__ = (
        Index('account_access_log_idx', location),
        Index('people_access_log_idx', access_from),
    )

    def get_date(self, request):
        """ Return activity date in a translated human readable format. """
        return format_datetime(request.locale_name, self.timestamp)


class PeopleVirtualAccount(Base):
    __tablename__ = 'virtual_people'
    id = Column(Integer, unique=True, primary_key=True)
    username = Column(UnicodeText(), unique=True, nullable=False)
    parent = Column(Integer, ForeignKey('people.id'), nullable=False)
    type = Column(Integer, default=1)
    last_logged = Column(DateTime, default=datetime.datetime.utcnow)
