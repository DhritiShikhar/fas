import turbogears
from turbogears import controllers, expose, paginate, identity, redirect, widgets, validate, validators, error_handler
from turbogears.database import session

import cherrypy

from fas.auth import *

from textwrap import dedent

import re

class JsonRequest(controllers.Controller):
    def __init__(self):
        '''Create a JsonRequest Controller.'''

    @expose("json")
    def index(self):
        '''Perhaps show a nice explanatory message about groups here?'''
        return dict(help='This is a json interface')
    
    @expose("json", allow_json=True)
    def group_list(self, search='*'):
        re_search = re.sub(r'\*', r'%', search).lower()
        groups = Groups.query.filter(Groups.name.like(re_search)).order_by('name')
        group_list = {}
        return dict(groups=groups)
        
    @expose("json", allow_json=True)
    def people_list(self, search='*'):
        re_search = re.sub(r'\*', r'%', search).lower()
        people = People.query.filter(People.username.like(re_search)).order_by('username')
        return dict(people=people)

