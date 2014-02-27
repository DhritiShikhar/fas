# -*- coding: utf-8 -*-

from pyramid.response import Response
from pyramid.view import view_config

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
)

from sqlalchemy.exc import DBAPIError

from pyramid.view import (
    view_config,
    forbidden_view_config,
)

from pyramid.security import (
    remember,
    forget,
    authenticated_userid,
)

from fas.models import DBSession
import fas.models.provider as provider


@view_config(route_name='api_home', renderer='/api_home.xhtml')
def api_home(request):
    return {}


@view_config(route_name='api_user_get', renderer='json')
def api_user_get(request):
    key = request.matchdict.get('key')
    value = request.matchdict.get('value')
    if key not in ['id', 'username', 'email', 'ircnick']:
        raise HTTPNotFound(
            {"error": "Bad request, no '%s' allowed" % key}
        )
    method = getattr(provider, 'get_people_by_%s' % key)
    user = method(DBSession, value)
    if not user:
        raise HTTPNotFound(
            {"error": "No such user %r" % value}
        )

    return user.to_json()


@view_config(route_name='api_group_get', renderer='json')
def api_group_get(request):
    key = request.matchdict.get('key')
    value = request.matchdict.get('value')
    if key not in ['id', 'name']:
        raise HTTPNotFound(
            {"error": "Bad request, no '%s' allowed" % key}
        )
    method = getattr(provider, 'get_group_by_%s' % key)
    group = method(DBSession, value)
    if not group:
        raise HTTPNotFound(
            {"error": "No such group %r" % value}
        )

    return group.to_json()

