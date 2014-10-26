# -*- coding: utf-8 -*-

from wtforms import (
    Form,
    StringField,
    TextAreaField,
    IntegerField,
    BooleanField,
    validators
    )

from fas.utils import _


class EditLicenseForm(Form):
    """ Form to  add, edit and validate license agreement infos."""
    name = StringField(_(u'Name'), [validators.Required()])
    content = TextAreaField(_(u'Text'), [validators.Required()])
    comment = StringField(_(u'Comments'), [validators.Optional()])


class SignLicenseForm(Form):
    """ Form to validate signed license agreement from registered people."""
    license = IntegerField(_(u'License Agreement'), [validators.Optional()])
    people = IntegerField(_(u'People Id'), [validators.Optional()])
    signed = BooleanField(_(u'I agree to the terms of the license'),
        [validators.Required()])
