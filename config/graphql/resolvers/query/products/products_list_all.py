from flask_app import db

from models.products import Products

from config.graphql.init import query

from schemas.serialization import SchemaSerializeProductsTimes


@query.field('productsListAll')
def resolve_productsListAll(_obj, _info):

  try:
    products = db.session.scalars(
      db.select(Products)
    )
    return SchemaSerializeProductsTimes(many = True).dump(products)

  except:
    pass

  return []
