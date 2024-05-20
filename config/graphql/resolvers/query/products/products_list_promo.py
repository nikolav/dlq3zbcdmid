import os
import random

from models.users          import Users
from config.graphql.init   import query
from schemas.serialization import SchemaSerializeProductsTimes

PACKAGES_LIST_PROMO_GOLD_MAX   = int(os.getenv('PACKAGES_LIST_PROMO_GOLD_MAX'))
PACKAGES_LIST_PROMO_SILVER_MAX = int(os.getenv('PACKAGES_LIST_PROMO_SILVER_MAX'))


@query.field('productsListPromo')
def resolve_productsListPromo(_obj, _info):
  lspromo        = []
  lspromo_silver = []
  lspromo_gold   = []
  
  try:
    
    # from users:gold
    for ugold in Users.pasckages_list_is_gold():
      # get MAX random promoted items
      lspromo_gold.extend(
        sorted(
          filter(
            lambda p: p.packages_is_promoted(),
            ugold.products
          ),
          key = lambda p: random.random()
        )[:PACKAGES_LIST_PROMO_GOLD_MAX]
      )
    random.shuffle(lspromo_gold)

    # from users:silver
    for usilver in Users.pasckages_list_is_silver():
      # get MAX random promoted items
      lspromo_silver.extend(
        sorted(
          filter(
            lambda p: p.packages_is_promoted(),
            usilver.products
          ),
          key = lambda p: random.random()
        )[:PACKAGES_LIST_PROMO_SILVER_MAX]
      )
    random.shuffle(lspromo_silver)

    lspromo.extend(lspromo_gold)
    lspromo.extend(lspromo_silver)
    
    return SchemaSerializeProductsTimes(many = True).dump(lspromo)

  except Exception as err:
    raise err

  return []
