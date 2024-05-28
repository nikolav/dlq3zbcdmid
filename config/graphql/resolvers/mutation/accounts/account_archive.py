from flask import g

from flask_app           import db
from models.users        import Users
from config.graphql.init import mutation


@mutation.field('accountsArchive')
def resolve_accountsArchive(_o, _i, uid):
  
  try:    
    u = db.session.get(Users, uid)
    
    if u.id == g.user.id:
      u.set_is_archived(True)
      
  except Exception as err:
    raise err
    
  else:
    return uid
  
  return None

