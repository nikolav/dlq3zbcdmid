from sqlalchemy import func
from sqlalchemy import desc

from flask_app import db

from models          import ln_orders_products
from models.products import Products
from models.orders   import Orders

from config import DEFAULT_POPULAR_PRODUCTS_LIMIT

from config.graphql.init import query

from schemas.serialization import SchemaSerializeProductsTimes


@query.field('productsListPopular')
def resolve_productsListPopular(_obj, _info, length = DEFAULT_POPULAR_PRODUCTS_LIMIT):
  try:
    pop_products = db.session.scalars(
      db.select(Products)
        .join(ln_orders_products)
        .join(Orders)
        .group_by(Products)
        .order_by(desc(func.sum(ln_orders_products.c.amount)))
        .limit(length)
    )
    return SchemaSerializeProductsTimes(many = True).dump(pop_products)

  except:
    pass

  return []
