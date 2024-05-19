from flask_app import db

from config.graphql.init import query
from models.products     import Products


@query.field('packagesIsPromoted')
def resolve_packagesIsPromoted(_obj, _info, pid):
  try:
    p = db.session.get(Products, pid)
    return p.packages_is_promoted() if p else False
  
  except Exception as err:
    raise err
    # pass
  
  return False
