# -*- coding: utf-8 -*-

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest

import fas.models.provider as provider

from fas.views import redirect_to
from fas.utils import compute_list_pages_from


@view_config(route_name='people')
def index(request):
    """ People list landing page. """
    return redirect_to('/people/page/1')


@view_config(route_name='people-paging', renderer='/people/list.xhtml')
def paging(request):
    """ People list's view with paging. """
    try:
        page = int(request.matchdict.get('pagenb', 1))
    except ValueError:
        return HTTPBadRequest()

    #TODO: get limit from config file or let user choose in between
    #TODO: predefined one?
    people = provider.get_people(50, page)

    pages, count = compute_list_pages_from('people', 50)

    if page > pages:
        return HTTPBadRequest()

    return dict(
        request=request,
        people=people,
        count=count,
        page=page,
        pages=pages
        )


@view_config(route_name='people-profile', renderer='/people/profile.xhtml')
def profile(request):
    """ People profile page. """
    try:
        id = request.matchdict['id']
    except KeyError:
        return HTTPBadRequest()

    person = provider.get_people_by_id(id)

    return dict(person=person, membership=person.group_membership)