# ordersReceivedProducts
from flask import g

from flask_app import db

from config.graphql.init import query

from models          import ln_orders_products
from models.products import Products
from models.orders   import Orders

from schemas.serialization import SchemaSerializeProductsTimes


@query.field('ordersReceivedProducts')
def resolve_ordersReceivedProducts(_obj, _info, order_id):
  ls = []
  try:
    res = db.session.execute(
      db.select(Products, ln_orders_products.c.amount)
        .join(ln_orders_products)
        .join(Orders)
        .where(Orders.id == order_id, Products.user_id == g.user.id)
    )
    for p, amount in res:
      node = SchemaSerializeProductsTimes().dump(p)
      node.update({ 'amount': amount })
      ls.append(node)

  except Exception as err:
    raise err
  
  return ls
