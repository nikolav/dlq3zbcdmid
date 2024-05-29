from flask import g

from flask_app import db

from models.users        import Users
from config.graphql.init import mutation


@mutation.field('accountsUpgradeUserCompany')
def resolve_accountsUpgradeUserCompany(_o, _i, uid):
  try:
    u = db.session.get(Users, uid)

    if not u.id == g.user.id:
      raise Exception('--resolve_accountsUpgradeUserCompany')

    u.accounts_upgrade(True)
    
  except Exception as err:
    raise err
    
  else:
    return str(uid)
  
  return None
