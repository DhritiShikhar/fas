# -*- coding: utf-8 -*-
import turbogears
from turbogears import controllers, expose, paginate, identity, redirect, widgets, validate, validators, error_handler
from turbogears.database import session

import turbogears.widgets as w
import cherrypy

from genshi.template.plugin import TextTemplateEnginePlugin

import fas.sidebar as sidebar
import logging
import fas.plugin as plugin

class LabelFixed(w.Label):
    '''the Turbogears Label Widget doesn't support predefined contents

    This wraps it and fixes that problem'''
    def render(self, value='', **keys):
        if not value:
            value = self.value
        return super(w.Label, self).render(value=value, **keys)

class SurveyPlugin(controllers.Controller):
    capabilities = ['survey_plugin']

    def __init__(self):
        '''Create a Survey Controller.'''
        self.path = ''

    @expose(template="fas_survey.templates.index")
    def index(self):
        value = "my Val"
        return dict(value=value)

    def join_survey(self, func, *args):
        ret = func(*args)
        if 'plugins' not in ret:
            ret['plugins'] = dict()
        ret['plugins']['survey'] = list()
        label = LabelFixed('survey_reason_label', 
                        attrs={'for':'survey_reason'})
        label.value = 'Reason for joining:'
        ret['plugins']['survey'].append(label)
        options = [('monkey', 'Monkey Salad'), ('cowbell', 'Moar Cowbell!')]
        selector = w.SingleSelectField('reason', options=options)
        ret['plugins']['survey'].append(selector)
        return ret
        pass

    def fill_join_survey(self, func, *args, **keys):
        print func
        print str(args)
        print str(keys)
        ret = func(*args)
        print ret
        return ret

    @classmethod
    def initPlugin(cls, controller):
        cls.log = logging.getLogger('plugin.survey')
        cls.log.info('Survey plugin initializing')
        try:
            path, self = controller.requestpath(cls, '/survey')
            cls.log.info('Survey plugin hooked')
            self.path = path
            if self.sidebarentries not in sidebar.entryfuncs:
                sidebar.entryfuncs.append(self.sidebarentries)
            plugin.plugin(self.join_survey, controller.user.new, 'survey')
            plugin.plugin(self.fill_join_survey, controller.user.create, 'survey')
        except (plugin.BadPathException,
            plugin.PathUnavailableException), e:
            cls.log.info('Survey plugin hook failure: %s' % e)

    def delPlugin(self, controller):
        self.log.info('Survey plugin shutting down')
        if self.sidebarentries in sidebar.entryfuncs:
            sidebar.entryfuncs.remove(self.sidebarentries)
            
    def sidebarentries(self):
        return [('Survey plugin', self.path)]
