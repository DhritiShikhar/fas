import turbogears
from turbogears import controllers, expose, paginate, identity, redirect, widgets, validate, validators, error_handler

import ldap

import os
import re
import gpgme
import StringIO

from fas.model import People
from fas.model import PersonEmails

from fas.auth import *

from textwrap import dedent

from random import Random
import sha
from base64 import b64encode


class knownUser(validators.FancyValidator):
    '''Make sure that a user already exists'''
    def _to_python(self, value, state):
        return value.strip()
    def validate_python(self, value, state):
        try:
            p = People.by_username(value)
        except InvalidRequestError:
            raise validators.Invalid(_("'%s' does not exist.") % value, value, state)

class nonFedoraEmail(validators.FancyValidator):
    '''Make sure that an email address is not @fedoraproject.org'''
    def _to_python(self, value, state):
        return value.strip()
    def validate_python(self, value, state):
        if value.endswith('@fedoraproject.org'):
            raise validators.Invalid(_("To prevent email loops, your email address cannot be @fedoraproject.org."), value, state)

class unknownUser(validators.FancyValidator):
    '''Make sure that a user doesn't already exist'''
    def _to_python(self, value, state):
        return value.strip()
    def validate_python(self, value, state):
        try:
            p = People.by_username(value)
        except InvalidRequestError:
            return
        except:
            raise validators.Invalid(_("Error: Could not create - '%s'") % value, value, state)
        
        raise validators.Invalid(_("'%s' already exists.") % value, value, state)
            
class userNameAllowed(validators.FancyValidator):
    '''Make sure that a username isn't blacklisted'''
    def _to_python(self, value, state):
        return value.strip()
    def validate_python(self, value, state):
        username_blacklist = config.get('username_blacklist')
        if re.compile(username_blacklist).match(value):
          raise validators.Invalid(_("'%s' is an illegal username.") % value, value, state)

class editUser(validators.Schema):
    username = validators.All(knownUser(not_empty=True, max=32), validators.String(max=32, min=3))
    human_name = validators.String(not_empty=True, max=42)
    #mail = validators.All(
    #    validators.Email(not_empty=True, strip=True, max=128),
    #    nonFedoraEmail(not_empty=True, strip=True, max=128),
    #)
    #fedoraPersonBugzillaMail = validators.Email(strip=True, max=128)
    #fedoraPersonKeyId- Save this one for later :)
    telephone = validators.PhoneNumber(max=24)
    postal_address = validators.String(max=512)
    
class newUser(validators.Schema):
    username = validators.All(
        unknownUser(not_empty=True, max=10),
        userNameAllowed(not_empty=True),
        validators.String(max=32, min=3),
    )
    human_name = validators.String(not_empty=True, max=42)
    email = validators.All(
        validators.Email(not_empty=True, strip=True),
        nonFedoraEmail(not_empty=True, strip=True),
    )
    #fedoraPersonBugzillaMail = validators.Email(strip=True)
    telephone = validators.PhoneNumber()
    postal_address = validators.String(max=512)

class changePass(validators.Schema):
    currentpassword = validators.String()
    # TODO (after we're done with most testing): Add complexity requirements?
    password = validators.String(min=8)
    passwordcheck = validators.String()
    chained_validators = [validators.FieldsMatch('password', 'passwordcheck')]

class userNameExists(validators.Schema):
    userName = validators.All(knownUser(max=10), validators.String(max=32, min=3))
    
def generatePassword(password=None,length=14,salt=''):
    ''' Generate Password '''
    secret = {} # contains both hash and password

    if not password:
        rand = Random() 
        password = ''
        # Exclude 0,O and l,1
        righthand = '23456qwertasdfgzxcvbQWERTASDFGZXCVB'
        lefthand = '789yuiophjknmYUIPHJKLNM'
        for i in range(length):
            if i%2:
                password = password + rand.choice(lefthand)
            else:
                password = password + rand.choice(righthand)
    
#    ctx = sha.new(password)
#    ctx.update(salt)
#    secret['hash'] = "{SSHA}%s" % b64encode(ctx.digest() + salt)
    secret['pass'] = password

    return secret


class User(controllers.Controller):

    def __init__(self):
        '''Create a User Controller.
        '''

    @identity.require(turbogears.identity.not_anonymous())
    def index(self):
        '''Redirect to view
        '''
        turbogears.redirect('/user/view/%s' % turbogears.identity.current.user_name)

    @expose(template="fas.templates.error")
    def error(self, tg_errors=None):
        '''Show a friendly error message'''
        if not tg_errors:
            turbogears.redirect('/')
        return dict(tg_errors=tg_errors)

    @identity.require(turbogears.identity.not_anonymous())
    @validate(validators=userNameExists())
    @error_handler(error)
    @expose(template="fas.templates.user.view")
    def view(self, userName=None):
        '''View a User.
        '''
        if not userName:
            userName = turbogears.identity.current.user_name
        if turbogears.identity.current.user_name == userName:
            personal = True
        else:
            personal = False
        if isAdmin(turbogears.identity.current.user_name):
            admin = True
        else:
            admin = False
        user = People.by_username(userName)
        groups = []
        for group in user.roles:
            groups.append(Groups.by_name(group.group.name))
#        groupsPending = Groups.byUserName(userName, unapprovedOnly=True)
        groupsPending = []
        groupdata={}
        groupUnapproved={}
        #for g in groups:
            #groupdata[g] = Groups.groups(g)[g]
            #unapproved = Groups.byGroupName(g, unapprovedOnly=True)
            #unapproved = [(v,k) for k,v in unapproved.items()]
            #unapproved.sort(date_compare)
            #unapproved.reverse()
            #groupUnapproved[g] = [(Person.byUserName(k).givenName,v) for v,k in unapproved]
#        for g in groupsPending:
#            groupdata[g] = Groups.groups(g)[g]
        try:
            g = Groups.by_name('cla_done')
            if g in user.memberships:
                claDone=True
            else:
                claDone=False
        except InvalidRequestError:
            claDone=None
        return dict(user=user, groups=groups, groupsPending=groupsPending, groupdata=groupdata, groupUnapproved=groupUnapproved, claDone=claDone, personal=personal, admin=admin)

    @identity.require(turbogears.identity.not_anonymous())
#    @validate(validators=userNameExists())
#    @error_handler(error)
    @expose(template="fas.templates.user.edit")
    def edit(self, username=None):
        '''Edit a user
        '''
        if not username:
            username = turbogears.identity.current.user_name
        if not canEditUser(turbogears.identity.current.user_name, username):
            turbogears.flash(_('You cannot edit %s') % username )
            username = turbogears.identity.current.username
        user = People.by_username(username)
    
        return dict(user=user)

    @identity.require(turbogears.identity.not_anonymous())
    @validate(validators=editUser())
    @error_handler(error)
    @expose(template='fas.templates.user.edit')
    def save(self, username, human_name, telephone, postal_address, email, ircnick=None, gpg_keyid=None, comments='', timezone='UTC'):
        if not canEditUser(turbogears.identity.current.user_name, username):
            turbogears.flash(_("You do not have permission to edit '%s'" % username))
            turbogears.redirect('/user/edit/%s', turbogears.identity.current.user_name)
            return dict()
        user = People.by_username(username)
        try:
            user.human_name = human_name
            user.emails['primary'].email = email
#            user.emails['bugzilla'] = PersonEmails(primary=bugzilla)
            user.ircnick = ircnick
#            user.gpg_keyid = gpg_keyid
            user.telephone = telephone
            user.postal_address = postal_address
            user.comments = comments
            user.timezone = timezone
        except TypeError:
            turbogears.flash(_('Your account details could not be saved: %s' % e))
        else:
            turbogears.flash(_('Your account details have been saved.'))
            turbogears.redirect("/user/view/%s" % username)
        return dict(user=user)

    @identity.require(turbogears.identity.in_group("accounts")) #TODO: Use auth.py
    @expose(template="fas.templates.user.list")
    def list(self, search="a*"):
        '''List users
        '''
        people = People.query.filter(People.username.like('%%%s%%' % username))
        try:
            people[0]
        except:
            turbogears.flash(_("No users found matching '%s'") % search)
            people = []
        return dict(users=users, search=search)
       
    @expose(template='fas.templates.user.new')
    def new(self):
        if turbogears.identity.not_anonymous():
            turbogears.flash(_('No need to sign up, you have an account!'))
            turbogears.redirect('/user/view/%s' % turbogears.identity.current.user_name)
        return dict()

    @validate(validators=newUser())
    @error_handler(error)
    @expose(template='fas.templates.new')
    # Kill mail for now.
    def create(self, username, human_name, email, telephone, postal_address):
        # TODO: Ensure that e-mails are unique- this should probably be done in the LDAP schema.
        #       Also, perhaps implement a timeout- delete account
        #           if the e-mail is not verified (i.e. the person changes
        #           their password) withing X days.  
        import turbomail
        try:
            p = People(username=username,
                human_name=human_name,
                telephone=telephone,
                password='*')
            p.emails['primary'] = PersonEmails(email=email, purpose='primary')

            newpass = generatePassword()
            message = turbomail.Message(config.get('accounts_mail'), p.emails['primary'].email, _('Fedora Project Password Reset'))
            message.plain = _(dedent('''
                 You have created a new Fedora account!
                 Your new password is: %s

                 Please go to https://admin.fedoraproject.org/fas/ to change it.
                 ''') % newpass['pass'])
            turbomail.enqueue(message)
            p.password = newpass['pass']
            turbogears.flash(_('Your password has been emailed to you.  Please log in with it and change your password'))
            turbogears.redirect('/login')
        except KeyError:
            turbogears.flash(_("The username '%s' already Exists.  Please choose a different username.") % username)
            turbogears.redirect('/user/new')
        return dict()

    @identity.require(turbogears.identity.not_anonymous())
    @expose(template="fas.templates.user.changepass")
    def changepass(self):
        return dict()

    @identity.require(turbogears.identity.not_anonymous())
    @validate(validators=changePass())
    @error_handler(error)
    @expose(template="fas.templates.user.changepass")
    def setpass(self, currentpassword, password, passwordcheck):
        p  = People.by_username(turbogears.identity.current.user_name)
        if not p.password == currentpassword:
            turbogears.flash('Your current password did not match')
            return dict()
        newpass = generatePassword(password)
        try:
            p.password = newpass['pass']
            turbogears.flash(_("Your password has been changed."))
        except:
            turbogears.flash(_("Your password could not be changed."))
        return dict()

    @expose(template="fas.templates.user.resetpass")
    def resetpass(self):
        if turbogears.identity.not_anonymous():
            turbogears.flash(_('You are already logged in!'))
            turbogears.redirect('/user/view/%s' % turbogears.identity.current.user_name)
        return dict()
            
    @expose(template="fas.templates.user.resetpass")
    def sendpass(self, username, email, encrypted=False):
        import turbomail
        # Logged in
        if turbogears.identity.current.user_name:
            turbogears.flash(_("You are already logged in."))
            turbogears.redirect('/user/view/%s', turbogears.identity.current.user_name)
            return dict()
        p = People.by_username(username)
        if username and email:
            if not email == p.emails['primary'].email:
                turbogears.flash(_("username + email combo unknown."))
                return dict()
            newpass = generatePassword()
            message = turbomail.Message(config.get('accounts_mail'), email, _('Fedora Project Password Reset'))
            mail = _(dedent('''
                You have requested a password reset!
                Your new password is: %s
                
                Please go to https://admin.fedoraproject.org/fas/ to change it.
                ''')) % newpass['pass']
            if encrypted:
                try:
                    plaintext = StringIO.StringIO(mail)
                    ciphertext = StringIO.StringIO()
                    ctx = gpgme.Context()
                    ctx.armor = True
                    signer = ctx.get_key(re.sub('\s', '', config.get('gpg_fingerprint')))
                    ctx.signers = [signer]
                    recipient = ctx.get_key(re.sub('\s', '', p.fedoraPersonKeyId))
                    def passphrase_cb(uid_hint, passphrase_info, prev_was_bad, fd):
                        os.write(fd, '%s\n' % config.get('gpg_passphrase'))
                    ctx.passphrase_cb = passphrase_cb
                    ctx.encrypt_sign([recipient],
                        gpgme.ENCRYPT_ALWAYS_TRUST,
                        plaintext,
                        ciphertext)
                    message.plain = ciphertext.getvalue()
                except:
                    turbogears.flash(_('Your password reset email could not be encrypted.  Your password has not been changed.'))
                    return dict()
            else:
                message.plain = mail;
            turbomail.enqueue(message)
            try:
                p.password = newpass['hash']
                turbogears.flash(_('Your new password has been emailed to you.'))
            except:
                turbogears.flash(_('Your password could not be reset.'))
            else:
                turbogears.redirect('/login')  
        return dict()

    @identity.require(turbogears.identity.not_anonymous())
    @expose(template="genshi-text:fas.templates.user.cert", format="text", content_type='text/plain; charset=utf-8')
    def gencert(self):
      from fas.openssl_fas import *
      user = Person.by_username(turbogears.identity.current.user_name)
      user.certificate_serial = int(user.certificate_serial) + 1

      pkey = createKeyPair(TYPE_RSA, 1024);

      digest = config.get('openssl_digest')
      expire = config.get('openssl_expire')
      cafile = config.get('openssl_ca_file')

      cakey = retrieve_key_from_file(cafile)
      cacert = retrieve_cert_from_file(cafile)

      req = createCertRequest(pkey, digest=digest,
          C=config.get('openssl_c'),
          ST=config.get('openssl_st'),
          L=config.get('openssl_l'),
          O=config.get('openssl_o'),
          OU=config.get('openssl_ou'),
          CN=user.cn,
          emailAddress=user.mail,
          )

      cert = createCertificate(req, (cacert, cakey), int(user.certificate_serial), (0, expire), digest='md5')
      certdump = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
      keydump = crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey)
      return dict(cert=certdump, key=keydump)

    # Not sure where to take this yet.
    @expose(format="json")
    def search(self, username=None, groupname=None):
        people = People.query.filter(People.username.like('%%%s%%' % username))
        return dict(people=people)

