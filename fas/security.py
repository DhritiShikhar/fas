# -*- coding: utf-8 -*-

import os
import hashlib
import fas.models.provider as provider

USERS = {'admin':'admin',
          'viewer':'viewer'}
GROUPS = {'admin':['group:admin']}


def groupfinder(userid, request):
    if userid in USERS:
        return GROUPS.get(userid, [])


def generate_token():
    """ Generate an API token. """
    return hashlib.sha1(os.urandom(256)).hexdigest()


class Base:

    def __init__(self):
        self.dbsession = None
        self.people = None
        self.token = None
        self.msg = ()

    def set_msg(self, name, text=''):
        self.msg = (name, text)

    def get_msg(self):
        return self.msg


class PasswordValidator(Base):
    pass


class OtpValidator(Base):
    pass


class QAValidator(Base):
    pass


class TokenValidator(Base):

    def __init__(self, apikey):
        self.token = apikey
        self.perms = 0
        self.msg = ''

    def is_valid(self):
        """ Check that api's key is valid. """
        self.msg = {'', ''}
        key = provider.get_account_permissions_by_token(self.token)
        if key:
            self.perms = key.permissions
            self.people = key.people
            return True
        else:
            self.msg = ('Access denied.', 'Unauthorized API key.')
        return False

    def set_token(self, token):
        """ Set token for validation. """
        self.token = token

    def get_perms(self):
        """ Get token related permissions. """
        return int(self.perms)

    def get_people_id(self):
        """ Get People's ID from validated token. """
        return self.people


class ParamsValidator(Base):

    def __init__(self, request, check_apikey=False):
        self.request = request
        self.params = []
        self.apikey = ''
        # maybe we should let admin configure this limit?
        self.limit = 200
        self.pagenumber = 1
        self.optional_params = []
        self.msg = ()

        if check_apikey:
            self.params.append(u'apikey')

    def __set_msg__(self, name, text=''):
        self.msg = (name, text)

    def add_optional(self, optional):
        """ Add optional parameter to validate.

        :args optional: string, requested optional parameter.
        """
        self.optional_params.append(unicode(optional))

    def add_param(self, params):
        """ Add mandatory parameter to validate.

        :arg params: string, requested madatory parameter.
        """
        self.params.append(unicode(params))

    def is_valid(self):
        """ Check if request's parameters are valid.

        :returns: True if all given parameters are valid. False otherwise.
        """
        if self.optional_params:
            for p in self.optional_params:
                self.params.append(p)

        if self.request.params:
            for key, value in self.request.params.iteritems():
                if key not in self.params:
                    self.set_msg('Parameter Error.',
                                    'Invalid parameter: %r' % str(key))
                    return False
                else:
                    if not value and (key not in self.optional_params):
                        if key == 'apikey':
                            self.request.response.status = '401 Unauthorized'
                            self.set_msg('Access denied.',
                                            "Required API key is missing.")
                        else:
                            self.set_msg('Invalid parameters', '')
                        return False
                    if key == 'apikey':
                        self.apikey = value
                    elif key == 'limit':
                        self.limit = value
                    elif key == 'page':
                        self.pagenumber = value
            return True
        else:
            self.request.response.status = '400 bad request'
            self.set_msg('Parameter error.', 'No parameter(s) found.')
        return False

    def set_params(self, params):
        self.params.append(params)

    def get_optional(self, optional):
        """ Get request optional param value."""
        try:
            return self.request.params.getone(unicode(optional))
        except KeyError:
            return None

    def get_apikey(self):
        """ Get API key value from request parameter. """
        return str(self.apikey)

    def get_limit(self):
        """ Get items limit per requests. """
        return int(self.limit)

    def get_pagenumber(self):
        """ Get page index for pagination. """
        return int(self.pagenumber)

    def get_msg(self):
        """ Get error messages from a validation check.

        :returns: tuple object of error message if is_valid() is False,
                  None otherwise.
        """
        return self.msg