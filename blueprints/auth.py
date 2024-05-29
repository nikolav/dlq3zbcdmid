import os
import secrets
# from pprint import pprint

from flask      import Blueprint
from flask      import g
from flask      import request
from flask      import render_template
from flask_cors import CORS
from flask_mail import Message

from sqlalchemy import func

from flask_app      import db
from flask_app      import io
from flask_app      import mail

from models.users    import Users
from models.docs     import Docs
# from models.tags    import Tags

from utils.pw       import hash  as hashPassword
from utils.pw       import check as checkPassword
from utils.jwtToken import issueToken
from utils.jwtToken import setInvalid as tokenSetInvalid
from utils.jwtToken import encode_secret
from utils.jwtToken import decode_secret

from middleware.arguments    import arguments_schema
from schemas.validation.auth import SchemaAuthLogin
from schemas.validation.auth import SchemaAuthRegister
from schemas.validation.auth import SchemaAuthSocial
from schemas.validation.auth import SchemaEmailResetRequest
from schemas.validation.auth import SchemaEmailResetObnovaLozinke

TAG_COMPANY_PROFILE_prefix = os.getenv('TAG_COMPANY_PROFILE_prefix')
IOEVENT_AUTH_NEWUSER       = os.getenv('IOEVENT_AUTH_NEWUSER')
JWT_SECRET_PASSWORD_RESET  = os.getenv('JWT_SECRET_PASSWORD_RESET')

# router config
bp_auth = Blueprint('auth', __name__, url_prefix = '/auth')

# cors blueprints as wel for cross-domain requests
CORS(bp_auth)

@bp_auth.route('/register', methods = ('POST',))
@arguments_schema(SchemaAuthRegister())
def auth_register():

  email    = g.arguments['email']
  password = g.arguments['password']
  company  = g.arguments['company']
  
  token = ''
  error = '@error/auth:register'

  try:    
    # skip registered
    if (0 < db.session.scalar(
      db.select(func.count(Users.id))
        .where(Users.email == email)
    )):
      raise Exception('access denied')

    # email available
    #  register, save
    newUser = Users.create_user(
      email    = email, 
      password = password,
      company  = company,
    )
    
    # new user added, issue access-token
    token = issueToken({ 'id': newUser.id })
    
  except Exception as err:
    error = err
  
  else:
    # user registered, send token, 201
    if token:
      io.emit(IOEVENT_AUTH_NEWUSER)
      return { 'token': token }, 201
  
  # forbiden otherwise
  return { 'error': str(error) }, 403
  
  
@bp_auth.route('/login', methods = ('POST',))
@arguments_schema(SchemaAuthLogin())
def auth_login():
  email    = g.arguments['email']
  password = g.arguments['password']
  
  token   = ''
  error   = '@error/auth:login'

  
  try:
    # find user by `email`
    u = db.session.scalar(
      db.select(Users).where(Users.email == email)
    )
    
    # skip invalid credentials ~email ~password
    if not u:
      raise Exception('access denied')

    #
    # skip archived
    if u.is_archived():
      raise Exception('access denied')
    
    
    if not checkPassword(password, u.password):
      raise Exception('access denied')
    
    # app user valid here
    #  issue access token
    token = issueToken({ 'id': u.id })

  except Exception as err:
    error = err

  else:
    if token:
      return { 'token': token }, 200

  return { 'error': str(error) }, 401

@bp_auth.route('/social', methods = ('POST',))
def auth_social():
  # company?
  # auth
  #   email
  #   uid?
  #   photoURL?
  #   displayName?
  token      = ''
  error      = '@error/auth:social'
  user_added = False
  
  try:
    data      = request.get_json()
    auth_data = SchemaAuthSocial().load(data.get('auth'))
    
    # schema validated; authenticate authdata
    u = db.session.scalar(
      db.select(Users)
        .where(Users.email == auth_data['email'])
    )
    
    # 
    # skip archived
    if u and u.is_archived():
      raise Exception('access denied')
    
    
    if not u:
      u = Users.create_user(
        email    = auth_data['email'],
        password = auth_data['uid'] if 'uid' in auth_data else secrets.token_bytes(1024).hex(),
        company  = data.get('company', None)
      )
      user_added = True

    # issue token
    token = issueToken({ 'id' : u.id })
          
  except Exception as err:
    error = err
  
  else:

    try:
      # store social auth data
      
      doc_profile = Docs.by_doc_id(
        f'{TAG_COMPANY_PROFILE_prefix}{u.id}', create = True)
      
      d = doc_profile.data.copy()
      d['authProvider'] = auth_data
      
      doc_profile.data = d
      db.session.commit()

    except:
      pass

    # auth social valid, send token, 201
    if user_added and token:
      io.emit(IOEVENT_AUTH_NEWUSER)
    
    return { 'token': token }, 201
  
  # forbiden otherwise
  return { 'error': str(error) }, 403


@bp_auth.route('/logout', methods = ('POST',))
def auth_logout():
  error = '@error/auth:logout'
  try:
    tokenSetInvalid(g.access_token)
  except Exception as err:
    error = err
  else:
    return {}, 200
  
  return { 'error': str(error) }, 500
  
@bp_auth.route('/who', methods = ('GET',))
def auth_who():
  error = '@error/auth:who'
  try:
    # send user data
    return { 
      'id'            : g.user.id, 
      'email'         : g.user.email, 
      'company'       : g.user.is_company(),
      'approved'      : g.user.approved(),
      'silver'        : g.user.packages_is('silver'),
      'gold'          : g.user.packages_is('gold'),
      'admin'         : g.user.is_admin(),
      'archived'      : g.user.is_archived(),
      'email_verified': g.user.email_verified(),
    }, 200
  except Exception as err:
    error = err
  
  return { 'error': str(error) }, 500


@bp_auth.route('/password-reset-obnova-lozinke', methods = ('POST',))
def password_reset_obnova_lozinke():

  d       = None
  payload = None
  
  try:
    d       = SchemaEmailResetObnovaLozinke().load(request.get_json())
    payload = decode_secret(d['key'], JWT_SECRET_PASSWORD_RESET)

    u = db.session.scalar(
      db.select(Users)
        .where(Users.email == payload['email'])
    )
    if not u:
      raise Exception('access denied --no-user')
    
    u.password = hashPassword(d['password'])
    db.session.commit()
    
  except Exception as err:
    raise err
    
  else:
    return payload['email'] if 'email' in payload else None
  
  return None

@bp_auth.route('/password-reset-email-link', methods = ('POST',))
def password_reset_email_link():
  
  d   = None
  res = None

  try:
    d = SchemaEmailResetRequest().load(request.get_json())

    if not Users.email_exists(d['email']):
      raise Exception('access denied --no-user')

  except Exception as err:
    raise err

  else:
    
    try:
      key = encode_secret({ 'email': d['email'] }, JWT_SECRET_PASSWORD_RESET)
      
      res = mail.send(
        Message(
          
          # subject
          'obnova-lozinke@kantar.rs',

          # from
          sender = ('KANTAR.RS', 'app@kantar.rs'),
          
          # default recepiens ls
          recipients = [d['email']],
          
          # pass all data to mail template
          html = render_template(
            'mail/password-reset-button-link.html', 
            url = f'{str(d['url']).rstrip("/")}/?key={key}')
        )
      )

    except Exception as err:
      raise 
    
    else:
      return d['email'] if not res else None
  
  return None
