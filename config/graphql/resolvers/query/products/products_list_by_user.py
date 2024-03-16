from flask_app import db

from models.users        import Users
from config.graphql.init import query

from schemas.serialization import SchemaSerializeProductsTimes


@query.field('productsListByUser')
def resolve_productsListByUser(_obj, _info, user_id):
  user = None
  com  = None

  try:
    user = db.session.get(Users, user_id)
    
    if not user:
      raise Exception('unavailable')

    if not user.is_company():
      raise Exception('unavailable')

    com = user
    
  except:
    pass

  else:
    if com:
      return SchemaSerializeProductsTimes(many = True).dump(com.products)

  return []

