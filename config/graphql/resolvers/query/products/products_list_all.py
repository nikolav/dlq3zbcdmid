from sqlalchemy.orm import joinedload
from flask_app import db

from models.tags import Tags
from models.users import Users
from models.products import Products
from models.docs import Docs

from config.graphql.init import query

from schemas.serialization import SchemaSerializeProductsTimes


@query.field('productsListAll')
def resolve_productsListAll(_obj, _info):

  try:
    products = db.session.scalars(
      db.select(Products)
        .options(
          joinedload(Products.tags), 
          joinedload(Products.user), 
          joinedload(Products.docs)
        )
    ).unique()
    return SchemaSerializeProductsTimes(many = True).dump(products)

  except Exception as err:
    raise err

  return []
