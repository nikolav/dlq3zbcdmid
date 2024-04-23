from sqlalchemy.orm import joinedload

from flask_app             import db
from models.products       import Products
from config.graphql.init   import query
from schemas.serialization import SchemaSerializeProductsTimes


@query.field('productsListExact')
def resolve_productsListExact(_obj, _info, products):
  ls_products = db.session.scalars(
    db.select(Products)
      # eager load .tags, .user
      .options(joinedload(Products.tags), joinedload(Products.user))
      .where(Products.id.in_(products))
  ).unique()
  return SchemaSerializeProductsTimes(many = True).dump(ls_products)
