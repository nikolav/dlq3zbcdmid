from flask import g
from flask_app import db

from models.users        import Users
from config.graphql.init import query

from schemas.serialization import SchemaSerializeProductsTimes


@query.field('productsListByUser')
def resolve_productsListByUser(_obj, _info, user_id):
  user = None

  try:
    user = g.user if user_id == g.user.id else db.session.get(Users, user_id)
    
    if not user:
      raise Exception('unavailable')

  except:
    pass

  else:
    if user:
      return SchemaSerializeProductsTimes(many = True).dump(user.products)

  return []

