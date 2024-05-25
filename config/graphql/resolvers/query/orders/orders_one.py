from flask_app             import db
from models.orders         import Orders
from schemas.serialization import SchemaSerializeOrdersTimes
from config.graphql.init   import query


@query.field('ordersOne')
def resolve_ordersOne(_o, _i, oid):
  try:
    return SchemaSerializeOrdersTimes().dump(db.session.get(Orders, oid))

  except Exception as err:
    raise err
    
  return None

