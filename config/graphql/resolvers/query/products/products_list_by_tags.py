from flask_app import db

from models.products     import Products
from models.tags         import Tags
from config.graphql.init import query

from schemas.serialization import SchemaSerializeProductsTimes


@query.field('productsListByTags')
def resolve_productsListByTags(_obj, _info, tags = []):
  try:
    return SchemaSerializeProductsTimes(many = True).dump(
        db.session.scalars(
          db.select(Products).join(Products.tags).where(Tags.tag.in_(tags))
        )
      )
    
  except:
    pass

  return []

