# from pprint import pprint

from flask_app             import db
from config.graphql.init   import query
from models.users          import Users
from schemas.serialization import SchemaSerializeOrdersTimes


@query.field('ordersListByUser')
def resolve_ordersListByUser(_obj, _info, uid):
  res = []
  try:
    u = db.session.get(Users, uid)
    if None == u:
      raise Exception('--unavailable')
    res = SchemaSerializeOrdersTimes(many = True).dump(u.orders)
  except Exception as err:
    raise err
  
  # pprint(res)
  return res
