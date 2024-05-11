from sqlalchemy import func
from sqlalchemy import desc

from flask_app import db

from models          import ln_orders_products
from models.products import Products

from config import DEFAULT_POPULAR_PRODUCTS_LIMIT

from config.graphql.init import query

from schemas.serialization import SchemaSerializeProductsTimes


@query.field('productsListPopular')
def resolve_productsListPopular(_obj, _info, length = DEFAULT_POPULAR_PRODUCTS_LIMIT):
  try:
    sumedc = func.sum(ln_orders_products.c.amount)
    pls = db.session.scalars(
      db.select(Products, sumedc)
        # .select_from(Products)
        .join(ln_orders_products)
        # .where(Products.id == ID)
        .group_by(Products.id)
        .order_by(desc(sumedc))
        .limit(length)
      )
    return SchemaSerializeProductsTimes(many = True).dump(pls)

  except:
    pass

  return []
