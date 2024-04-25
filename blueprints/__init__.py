import os

import sqlalchemy

from flask      import Blueprint
from flask_cors import CORS

from flask_app                   import db
from config                      import TAG_VARS
from models.tags                 import Tags
from models.docs                 import Docs
from models.users                import Users
from middleware.wrappers.timelog import timelog
from utils.jwtToken              import encode


ADMIN_EMAIL   = os.getenv('ADMIN_EMAIL')
USER_EMAIL    = os.getenv('USER_EMAIL')
POLICY_ADMINS = os.getenv('POLICY_ADMINS')

bp_home = Blueprint('home', __name__, url_prefix = '/')

# cors blueprints as wel for cross-domain requests
cors_bp_home = CORS(bp_home)

@bp_home.route('/', methods = ('GET',))
@timelog
def status_ok():
  
  admin_email = ''
  app_name    = ''
  
  
  for d in Docs.tagged(TAG_VARS):

    if 'app:name' in d.data:
      app_name = d.data['app:name']
      
    if 'admin:email' in d.data:
      admin_email = d.data['admin:email']
    
    if app_name and admin_email:
      break

  
  uid = db.session.scalar(
    db.select(Users.id)
    .where(Users.email == USER_EMAIL)
  )
  
  uid_admin = db.session.scalar(
    db.select(Users.id)
    .where(Users.email == ADMIN_EMAIL)
  )
  
  uids_admin = [u.id for u in Tags.by_name(POLICY_ADMINS).users]

  return {
    'status'        : 'ok',
    'app:name'      : app_name,
    'admin:email'   : admin_email,
    'admin:pin'     : uid_admin,
    'uid:default'   : uid,
    'token:default' : encode({ 'id': uid }),
    'sqlalchemy'    : sqlalchemy.__version__,
    'admins'        : uids_admin,
  }
