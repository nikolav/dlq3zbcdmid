import os
from flask_app           import io
from flask_app           import db
from models.orders       import Orders
from config.graphql.init import mutation


# IOEVENT_ORDERS_CHANGE = os.getenv('IOEVENT_ORDERS_CHANGE')
IOEVENT_ORDER_UPDATED = os.getenv('IOEVENT_ORDER_UPDATED')

@mutation.field('ordersSetCompleted')
def r_ordersSetCompleted(_o, _i, oid, completed = None):
  flag_initial = None
  
  try:
    o = db.session.get(Orders, oid)
    
    if not o:
      raise Exception('--r_ordersSetCompleted')
    
    flag_initial = o.completed
    
    o.completed = bool(completed)
    db.session.commit()

  except Exception as err:
    raise err
  
  else:
    if o.completed != flag_initial:
      io.emit(f'{IOEVENT_ORDER_UPDATED}{oid}')
    return str(oid)
  
  return None
