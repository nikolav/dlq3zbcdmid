
from flask import g
from sqlalchemy import desc

from flask_app import db

from config.graphql.init import query

from models          import ln_orders_products
from models.products import Products
from models.orders   import Orders

from schemas.serialization import SchemaSerializeOrdersTimes


@query.field('ordersReceived')
def resolve_ordersReceived(_obj, _info):
  try:
    orders = db.session.scalars(
      db.select(Orders)
        .join(ln_orders_products)
        .join(Products)
        .where(
          # pick orders for own items only
          Products.user_id == g.user.id
        )
        .order_by(desc(Orders.created_at))
        .group_by(Orders)
    )  
    return SchemaSerializeOrdersTimes(many = True).dump(orders)

  except:
    pass

  return []

