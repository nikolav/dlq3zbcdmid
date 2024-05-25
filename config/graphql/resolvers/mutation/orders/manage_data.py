import os

from flask_app import db
from flask_app import io

from config.graphql.init   import mutation
from models.orders         import Orders
from schemas.serialization import SchemaSerializeOrdersTimes

IOEVENT_ORDER_UPDATED = os.getenv('IOEVENT_ORDER_UPDATED')


@mutation.field('manageOrderData')
def resolve_manageOrderData(_obj, _info, oid, data):
  changes = 0
  try:
    o = db.session.get(Orders, oid)
    if not o:
      raise Exception('--invalid')
    
    status = data.get('status')
    print(status)
    # delivery  = data.get('delivery')
    # completed = data.get('completed')
    # canceled  = data.get('canceled')
    if status != o.status:
      o.status = status
      db.session.commit()
      changes += 1
    
  except Exception as err:
    raise err

  else:
    if 0 < changes:
      io.emit(f'{IOEVENT_ORDER_UPDATED}{oid}')
    
    return SchemaSerializeOrdersTimes().dump(o)

  return None
