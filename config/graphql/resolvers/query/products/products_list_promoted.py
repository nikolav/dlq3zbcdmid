import os

from flask_app import db

from models.tags import Tags
from models.users import Users
from models.products import Products
from models.docs import Docs

from config.graphql.init import query

from schemas.serialization import SchemaSerializeProductsTimes

POLICY_PACKAGE_PROMOTED = os.getenv('POLICY_PACKAGE_PROMOTED')
PACKAGES_LIST_ALL_MAX   = int(os.getenv('PACKAGES_LIST_ALL_MAX'))


SORTED_ORDER = {
  'silver': 100,
  'gold'  : 200,
}

def product_package_type(product):
  return 'gold' if product.user.packages_is('gold') else 'silver'


@query.field('productsListPromoted')
def resolve_productsListPromoted(_obj, _info):
  try:
    lsp = db.session.scalars(
      db.select(Products)
        .join(Products.tags)
        .where(Products.tags.any(
          Tags.tag == POLICY_PACKAGE_PROMOTED
        ))
        .limit(PACKAGES_LIST_ALL_MAX)
    ).unique()
    
    return SchemaSerializeProductsTimes(many = True).dump(
      sorted(lsp, key = lambda p: SORTED_ORDER.get(product_package_type(p), 0), reverse = True)
    )

  except Exception as err:
    raise err

  return []
