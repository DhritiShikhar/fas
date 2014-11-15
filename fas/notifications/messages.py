# -*- coding: utf-8 -*-


class Msg(object):

    def __init__(self, config):
        self.config = config

    def signature(self):
        """ Email signature template. """
        return u"""\
Regards,
-
The %(orga)s
""" % {'orga': self.config.get('project.organisation')}

    def account_update(self):
        """ Account messages template. """
        return {
            'registration': {
                'subject': u"""\
Confirm your %(organisation)s Account!""",
                'body': u"""\
Welcome to the %(organisation)s!

You are just one step away from contributing to a great FOSS community!

To complete your account creation, please visit this link:
%(url)s

%(sig)s
""",
                'fields': lambda **x: {
                    'organisation': x['organisation'],
                    'url': x['url'],
                    'sig': self.signature()
                    }
        },
            'password-reset': {
                'subject': u"""Password reset request on your account""",
                'body': u"""\
Hello %(fullname)s,

Someone (hopefully you) has requested a password reset for your account
`%(username)s` on the %(organisation)s Account System (FAS): %(url)s.

To complete this procedure, please visit this link:
%(validation_url)s

If you did not request this password change, simply disregard this email and
please contact a FAS administrator at: %(admin_email)s.
This email is sent only to the address on file for your account and will become
invalid after 24 hours.

%(sig)s
""",
                'fields': lambda **x: {
                    'fullname': x['people'].fullname,
                    'username': x['people'].username,
                    'organisation': x['organisation'],
                    'url': self.config.get('project.url'),
                    'validation_url': x['reset_url'],
                    'admin_email': self.config.get('project.admin.email'),
                    'sig': self.signature()
                    }
        },
        }

    def membership_update(self):
        """ Group membership messages template."""
        return {
            'invite': {
                'subject': u"""\
Invitation to join %(orga)s group %(groupname)s!""",
                'body': u"""\
%(fullname)s has invited you to join the %(orga)s by joining the group %(groupname)s!

We are a community of users and developers who produce a complete
operating system from entirely free and open source software (FOSS).

%(fullname)s thinks that you have knowledge and skills that make you a great fit
for the Fedora community, and that you might be interested in contributing.

How could you team up with the Fedora community to use and develop your skills?
Check out http://fedoraproject.org/join-fedora for some ideas.

Our community is more than just software developers
Fedora and FOSS are changing the world, come be a part of it!

%(sig)s
""",
                'fields': lambda **x: {
                    'fullname': x['people'].fullname,
                    'groupname': x['group'].name,
                    'url': x['url'],
                    'orga': x['organisation'],
                    'sig': self.signature()
                    }
            },

            'application': {
                'subject': u"""\
Your membership request for %(groupname)s is being reviewed""",
                'body': u"""\
Hello %(fullname)s,

Your request to be part of group %(groupname)s has been successfully
registered and will be review for approval as soon as possible by
an sponsor or administrator.

You can check your request status by visiting %(url)s.

%(sig)
""",
                'fields': lambda **x: {
                    'fullname': unicode(x['people'].fullname),
                    'groupname': unicode(x['group'].name),
                    'url': x['url'],
                    'sig': self.signature()
                    }
            },

            'join': {
                'subject': u"""Welcome to group %(groupname)s\!""",
                'body': u"""\
Hello %(fullname)s,

Thank you for joining group %(groupname)s.

Review your membership at %(url)s

%(sig)s
""",
                'fields': lambda **x: {
                    'fullname': unicode(x['people'].fullname),
                    'groupname': x['group'].name,
                    'url': x['url'],
                    'sig': self.signature()
                    }
            },

            'upgrade': {
                'subject': u"""\
You have been promoted to %(role)s in group %(groupname)s""",
                'body': u"""\
Congratulation %(fullname)s,

You have been upgraded to %(role)s into group %(groupname)s.
To review your new role and power visit %(url)s

%(sig)s
""",
            'fields': lambda **x: {
                'fullname': unicode(x['people'].fullname),
                'groupname': unicode(x['group'].name),
                'role': unicode(x['role'].name.lower()),
                'url': x['url'],
                'sig': self.signature()
                }
        },

            'downgrade': {
                'subject': u"""\
You have been demoted to %(role)s in group %(groupname)s""",
                'body': u"""\
Hello %(fullname)s,

this is to inform you that you have been downgraded to %(role)s
into group %(groupname)s.

%(sig)s
""",
                'fields': lambda **x: {
                    'fullname': unicode(x['people'].fullname),
                    'groupname': unicode(x['group'].name),
                    'role': x['role'].name.lower(),
                    'sig': self.signature()
                    }
            },

            'admin_change': {
                'subject': u"""\
Your have been promoted as the new principal administrator of %(groupname)s""",
                'body': u"""\
Hello %(fullname)s,

%(former_admin)s has made you the new principal administrator for group
%(groupname)s.

Review your new group information at %(url)s

%(sig)s
""",
                'fields': lambda **x: {
                    'fullname': unicode(x['people'].fullname),
                    'groupname': unicode(x['group'].name),
                    'former_admin': x['admin'].fullname,
                    'url': x['url'],
                    'sig': self.signature()
                    }
            },

            'revoke': {
                'subject': u"""You have been removed from group %(groupname)s""",
                'body_self_removal': u"""\
Hello %(fullname)s,

This is to inform you that you have been successfully removed from the
%(groupname)s group as requested.

%(sig)s
""",
                'body_admin_revoked': u'''\
Hello %(fullname)s,

This is to inform you that you have been removed from the group %(groupname)s
with the following reason:

%(reason)s

If you believe this action is not expected to be happened please, contact
an group\'s administrator or an account\'s administrator.

%(sig)s
''',
                'fields': lambda **x: {
                    'fullname': unicode(x['people'].fullname),
                    'groupname': unicode(x['group'].name),
                    'reason': x['reason'],
                    'sig': self.signature()
                    }
            },
        }