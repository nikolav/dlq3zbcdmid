import os

from flask      import Blueprint
from flask      import g
from flask_cors import CORS

from sqlalchemy import func

from flask_app      import db
from models.users   import Users
from models.tags    import Tags
from utils.pw       import hash  as hashPassword
from utils.pw       import check as checkPassword
from utils.jwtToken import issueToken
from utils.jwtToken import setInvalid as tokenSetInvalid

from middleware.arguments    import arguments_schema
from schemas.validation.auth import SchemaAuthLogin
from schemas.validation.auth import SchemaAuthRegister


# router config
bp_auth = Blueprint('auth', __name__, url_prefix = '/auth')

# cors blueprints as wel for cross-domain requests
cors_bp_auth = CORS(bp_auth)

@bp_auth.route('/register', methods = ('POST',))
@arguments_schema(SchemaAuthRegister())
def auth_register():

  email    = g.arguments['email']
  password = g.arguments['password']
  company  = g.arguments['company']
  
  token = ''
  error = '@error/internal.500'

  try:    
    # skip registered
    if (0 < db.session.scalar(
      db.select(func.count(Users.id)).where(Users.email == email)
    )):
      raise Exception('access denied')
        
    # email available
    #  register, save
    newUser = Users(email = email, password = hashPassword(password))
    db.session.add(newUser)

    db.session.commit()
    
    # if `bool:company == true` provided; --dev-feature
    #   tag user as company
    #   tag user as :approved
    #   tag user as fs:approved
    if company:
      newUser.tags.append(Tags.by_name(os.getenv('POLICY_COMPANY')))
      newUser.tags.append(Tags.by_name(os.getenv('POLICY_APPROVED')))
      newUser.tags.append(Tags.by_name(os.getenv('POLICY_FILESTORAGE')))
      db.session.commit()
    
    # new user added, issue access-token
    token = issueToken({ 'id': newUser.id })
    
  except Exception as err:
    error = err
  
  else:
    # user registered, send token, 201
    if token:
      return { 'token': token }, 201
  
  # forbiden otherwise
  return { 'error': str(error) }, 403
  
  
@bp_auth.route('/login', methods = ('POST',))
@arguments_schema(SchemaAuthLogin())
def auth_login():
  email    = g.arguments['email']
  password = g.arguments['password']
  
  token   = ''
  error   = '@error/internal.500'

  
  try:
    # find user by `email`
    u = db.session.scalar(
      db.select(Users).where(Users.email == email)
    )
    
    # skip invalid credentials ~email ~password
    if not u:
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


@bp_auth.route('/logout', methods = ('POST',))
def auth_logout():
  error = '@error/internal.500'
  try:
    tokenSetInvalid(g.access_token)
  except Exception as err:
    error = err
  else:
    return {}, 200
  
  return { 'error': str(error) }, 500
  
@bp_auth.route('/who', methods = ('GET',))
def auth_who():
  error = '@error/internal.500'
  try:
    # send user data
    return { 'id': g.user.id, 'email': g.user.email, 'company': g.is_company }, 200
  except Exception as err:
    error = err
  
  return { 'error': str(error) }, 500
