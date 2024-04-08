from flask_app import db

from models.products import Products

from config.graphql.init import query

from schemas.serialization import SchemaSerializeProductsTimes


@query.field('productsListExact')
def resolve_productsListExact(_obj, _info, products):
  try:
    ls_products = db.session.scalars(
      db.select(Products)
        .where(Products.id.in_(products))
    )
    return SchemaSerializeProductsTimes(many = True).dump(ls_products)

  except:
    pass

  return []
