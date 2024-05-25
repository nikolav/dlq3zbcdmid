
from flask_app import db

from config.graphql.init import query

from models          import ln_orders_products
from models.products import Products
from models.orders   import Orders


@query.field('getOrderProductsDeliveryDate')
def resolve_getOrderProductsDeliveryDate(_o, _i, oid, uid):
  data = {}
  try:
    res = db.session.execute(
      db.select(Products.id, ln_orders_products.c.delivery_at)
        .join(ln_orders_products)
        .join(Products.orders)
        .where(
          ln_orders_products.c.order_id == oid,
          ln_orders_products.c.product_id.in_(
            db.select(Products.id)
              .join(Products.orders)
              .where(
                Orders.id == oid,
                Products.user_id == uid
              )
              .subquery()
          )
        )
    )

    for pid, d in res:
      data[pid] = d
    
  except Exception as err:
    raise err

  return data
