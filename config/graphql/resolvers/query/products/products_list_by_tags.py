from flask_app import db

from models.products     import Products
from models.tags         import Tags
from config.graphql.init import query

from schemas.serialization import SchemaSerializeProductsTimes

PKG = {
  'silver' : 100, 
  'gold'   : 200,
}

@query.field('productsListByTags')
def resolve_productsListByTags(_obj, _info, tags = []):
  try:
    return SchemaSerializeProductsTimes(many = True).dump(
        sorted(
            db.session.scalars(
            db.select(Products)
              .join(Products.tags)
              .where(Tags.tag.in_(tags))
          ),
          key     = lambda p: PKG.get(p.packages_type(), 0),
          reverse = True
        ))
  
  except Exception as err:
    raise err
    # pass

  return []

