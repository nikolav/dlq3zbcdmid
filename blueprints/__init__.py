from flask      import Blueprint
from flask_cors import CORS

from config                      import TAG_VARS
from models.docs                 import Docs
from middleware.wrappers.timelog import timelog


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
    
  return {
    'status'      : 'ok',
    'app:name'    : app_name,
    'admin:email' : admin_email,
  }
