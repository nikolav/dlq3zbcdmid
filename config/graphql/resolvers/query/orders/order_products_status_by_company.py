
from config.graphql.init import query
from flask_app import db
from models.orders import Orders
from models.products import Products
from models import ln_orders_products

@query.field('getOrderProductsStatusByCompany')
def resolve_getOrderProductsStatusByCompany(_o, _i, oid, uid):
  result      = {}
  rows_result = []
  
  try:
    rows_result = db.session.execute(
      db.select(Products.id, ln_orders_products.c.status)
        .join(ln_orders_products)
        .join(Products.orders)
        .where(
          ln_orders_products.c.order_id   == oid,
          ln_orders_products.c.product_id.in_(
            db.select(Products.id)
              .join(Products.orders)          
              .where(
                Orders.id        == oid,
                Products.user_id == uid
              )
              .subquery()
          )
        )
    )
  
  except Exception as err:
    raise err
  
  else:
    for pid, s in rows_result:
      result[pid] = s
  
  return result

