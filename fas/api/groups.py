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
__author__ = ['Xavier Lamien <laxathom@fedoraproject.org>',
              'Pierre-Yves Chibon <pingou@fedoraproject.org>']

from pyramid.view import view_config

from . import (
    BadRequest,
    NotFound,
    MetaData
)
import fas.models.provider as provider
from fas.events import ApiRequest, GroupCreated
from fas.security import ParamsValidator
from fas.util import setup_group_form
from fas.models import register, MembershipStatus, MembershipRole, \
    AccountPermissionType
from fas import log


class GroupAPI(object):
    def __init__(self, request):
        self.request = request
        self.notify = self.request.registry.notify
        self.params = self.request.param_validator
        self.data = MetaData('Groups')
        self.perm = None
        self.notify(ApiRequest(self.request, self.data, self.perm))
        self.apikey = self.request.token_validator

    def __get_group__(self, key, value):
        if key not in ['id', 'name']:
            raise BadRequest('Invalid key: %s' % key)
        method = getattr(provider, 'get_group_by_%s' % key)
        group = method(value)
        if not group:
            raise NotFound('No such group: %s' % value)

        return group

    @view_config(
        route_name='api-group-list', renderer='json', request_method='GET')
    def group_list(self):
        """ Returns a JSON's output of registered group's list. """
        group = None

        self.params.add_optional('limit')
        self.params.add_optional('page')

        if self.apikey.validate():
            limit = self.params.get_limit()
            page = self.params.get_pagenumber()

            group = provider.get_groups(limit=limit, page=page)

        if group:
            groups = []
            for g in group:
                groups.append(g.to_json(self.apikey.get_perm()))

            self.data.set_pages(provider.get_groups(count=True), page, limit)
            self.data.set_data(groups)

        return self.data.get_metadata()

    @view_config(route_name='api-group-get', renderer='json', request_method='GET')
    def get_group(self):
        group = None

        if self.apikey.validate():
            key = self.request.matchdict.get('key')
            value = self.request.matchdict.get('value')

            try:
                group = self.__get_group__(key, value)
            except BadRequest as err:
                self.request.response.status = '400 bad request'
                self.data.set_error_msg('Bad request', err.message)
            except NotFound as err:
                self.data.set_error_msg('Item not found', err.message)
                self.request.response.status = '404 page not found'

        if group:
            self.data.set_data(group.to_json(self.apikey.get_perm()))

        return self.data.get_metadata()

    @view_config(
        route_name='api-group-types', renderer='json', request_method='GET')
    def get_group_type(self):
        group_types = provider.get_group_types()
        self.data.set_name('GroupTypes')

        if len(group_types) > 0:
            self.data.set_data([g.to_json() for g in group_types])
        else:
            self.data.set_error_msg('None items', 'There is no group types')

        return self.data.get_metadata()

    # @view_config(
    # route_name='api-group-edit', renderer='json', request_method='POST')
    # def edit_group(self):
    # key = self.request.matchdict.get('key')
    #     value = self.request.matchdict.get('value')
    #
    #     if self.apikey.validate():
    #         try:
    #             group = self.__get_group__(key, value)
    #         except BadRequest as err:
    #             self.request.response.status = '400 bad request'
    #             self.data.set_error_msg('Bad request', err.message)
    #         except NotFound as err:
    #             self.request.response.status = '404 page not found'
    #             self.data.set_error_msg('Item not found', err.message)
    #
    #         form = EditGroupForm(self.request.POST, group)
    #
    #         if form.validate():
    #             form.populate_obj(group)
    #             self.data.set_status('stored', 'User updated')
    #             self.data.set_data(group.to_json(self.apikey.get_perm()))
    #         else:
    #             self.request.response.status = '400 bad request'
    #             self.data.set_error_msg('Invalid request', form.errors)
    #
    #     return self.data.get_metadata()

    @view_config(
        route_name='api-group-edit', renderer='json', request_method='POST')
    def create_group(self):
        """ Create a group from an client's request.
        """
        if self.apikey.get_perm != AccountPermissionType.CAN_EDIT_GROUP_INFO:
            self.data.set_error_msg(self.apikey.get_msg())
            return self.data.get_metadata()

        form = setup_group_form(self.request)

        if self.request.method == 'POST':
            if form.validate():
                group = register.add_group(form)
                self.notify(GroupCreated(self.request, group))
                self.data.set_data(form.data)
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        log.error('Error in field %s: %s' % (
                            getattr(form, field).label.text,
                            error
                        ))
                        self.data.set_error_msg('Invalid data', '%s: %s' %
                                                (getattr(form, field).label.text,
                                                 error))

        return self.data.get_metadata()
