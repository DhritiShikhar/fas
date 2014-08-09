# -*- coding: utf-8 -*-

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.security import NO_PERMISSION_REQUIRED

import fas.models.provider as provider
import fas.models.register as register

from fas.security import generate_token

from fas.views import redirect_to
from fas.utils import compute_list_pages_from

# temp import, i'm gonna move that away
from pyramid.httpexceptions import HTTPFound


class People(object):

    def __init__(self, request):
        self.request = request
        self.id = -1
        self.person = None

    def redirect_to_profile(self):
        return redirect_to('/people/profile/%s' % self.id)

    @view_config(route_name='people')
    def index(self):
        """ People list landing page. """
        return redirect_to('/people/page/1')

    @view_config(route_name='people-paging', renderer='/people/list.xhtml',
        permission=NO_PERMISSION_REQUIRED)
    def paging(self):
        """ People list's view with paging. """
        try:
            page = int(self.request.matchdict.get('pagenb', 1))
        except ValueError:
            return HTTPBadRequest()

        #TODO: get limit from config file or let user choose in between
        #      predefined one ?
        people = provider.get_people(50, page)

        pages, count = compute_list_pages_from('people', 50)

        if page > pages:
            return HTTPBadRequest()

        return dict(
            people=people,
            count=count,
            page=page,
            pages=pages
            )

    @view_config(route_name='people-profile', renderer='/people/profile.xhtml')
    def profile(self):
        """ People profile page. """
        try:
            _id = self.request.matchdict['id']
        except KeyError:
            return HTTPBadRequest()

        self.person = provider.get_people_by_id(_id)

        return dict(person=self.person, membership=self.person.group_membership)

    @view_config(route_name='people-activities',
        renderer='/people/activities.xhtml')
    def activities(self):
        """ People's activities page. """
        try:
            self.id = self.request.matchdict['id']
        except KeyError:
            return HTTPBadRequest()

        activities = provider.get_account_activities_by_people_id(self.id)

        # Prevent client/user from requesting direct url
        if len(activities) > 0:
            self.person = activities[0].person
            if self.request.authenticated_userid != self.person.username:
                return self.redirect_to_profile()
        else:
            if self.request.authenticated_userid != self.person.username\
            or self.request.authenticated_userid == self.person.username:
                return self.redirect_to_profile()

        return dict(activities=activities, person=self.person)

    @view_config(route_name='people-edit', permission='authenticated')
    def edit(self):
        """ Profile's edit page."""
        #TODO: move this to Auth provider
        #if self.request.authenticated_userid != person.username:
            #return redirect_to('/people/profile/%s' % _id)

        return Response('This is an empty edit page.')

    @view_config(route_name='people-token', permission='authenticated',
        renderer='/people/access-token.xhtml')
    def access_token(self):
        """ People's access token."""
        try:
            self.id = self.request.matchdict['id']
        except KeyError:
            return HTTPBadRequest()

        if 'form.save.token' in self.request.params:
            perm = self.request.params['permission']
            desc = self.request.params['description']

            token = generate_token()
            register.add_token(self.id, desc, token, perm)
            self.request.session.flash(token, 'tokens')

        if 'form.delete.token' in self.request.params:
            perm = self.request.params['form.delete.token']
            register.remove_token(perm)
            # prevent from printing out deleted token in url
            return HTTPFound(self.request.route_path(
            'people-token', id=self.id))

        perms = provider.get_account_permissions_by_people_id(self.id)

        # Prevent client/user from requesting direct url
        #TODO: move this to Auth provider?
        if len(perms) > 0:
            self.person = perms[0].account
            if self.request.authenticated_userid != self.person.username:
                return self.redirect_to_profile()
        else:
            if self.person:
                if self.request.authenticated_userid != self.person.username:
                    return self.redirect_to_profile()
            else:
                self.person = provider.get_people_by_id(self.id)

        return dict(permissions=perms, person=self.person)
