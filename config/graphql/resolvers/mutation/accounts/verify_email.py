import os
from flask import g
from config.graphql.init import mutation
from utils.jwtToken import decode_secret
from flask_app import db
from models.users import Users

JWT_SECRET_VERIFY_EMAIL = os.getenv('JWT_SECRET_VERIFY_EMAIL')


@mutation.field('accountsVeifyEmail')
def resolve_accountsVeifyEmail(_o, _i, data):

  try:
    # .uid .email
    payload = decode_secret(data.get('key'), JWT_SECRET_VERIFY_EMAIL)
    u = db.session.get(Users, payload['uid'])

    if not u.id == g.user.id:
      raise Exception('--resolve_accountsVeifyEmail')
    
    u.set_email_verified(True)  
    
  except Exception as err:
    raise err
  
  else:
    return u.email
  
  return None

