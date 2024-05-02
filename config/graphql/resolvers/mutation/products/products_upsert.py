import os

from flask import g

from flask_app import db
from flask_app import io

from models.tags  import Tags
from models.products import Products
from config.graphql.init import mutation
from schemas.serialization import SchemaSerializeProductsTimes
# from middleware.authguard import authguard
from middleware.authguard import authguard_company_approved

IOEVENT_PRODUCTS_CHANGE_SINGLE_prefix = os.getenv('IOEVENT_PRODUCTS_CHANGE_SINGLE_prefix')
IOEVENT_PRODUCTS_CHANGE_prefix        = os.getenv('IOEVENT_PRODUCTS_CHANGE_prefix')
IOEVENT_PRODUCTS_CHANGE               = os.getenv('IOEVENT_PRODUCTS_CHANGE')
PRODUCT_CATEGORY_prefix               = os.getenv('PRODUCT_CATEGORY_prefix')


FIELDS = [
  'name',
  'category',
  'price',
  'stock',
  'stockType',
  'onSale',
  'description',
]

@mutation.field('productsUpsert')
@authguard_company_approved
def resolve_productsUpsert(_obj, _info, data, id = None):
  p = None

  try:
    p = db.session.get(Products, id) if None != id else None
    category_ = data.get('category', None)

    if None != p:
      # update
      
      # skip forbidden updates
      if not p.user.id == g.user.id:
        raise Exception('forbidden')
      
      for field in FIELDS:
        if 'category' != field:
          if field in data:
            if 'price' == field:
              priceNew = data['price']
              # if cache empty or doesnt match update
              if not len(p.price_history) or (priceNew != p.price_history[-1]['price']):
                if 0 <= priceNew:
                  p.price_history_add(priceNew)
            setattr(p, field, data[field])
        else:
          if not category_:
            continue

          if p.includes_tags(category_):
            continue
          # edit category 
          #   drop old tags
          #   add provided
          #  loop tags, drop if starts with category domain, `@product:category:`
          
          tags_rm = []
          for t in p.tags:
            if t.tag.startswith(PRODUCT_CATEGORY_prefix):
              tags_rm.append(t)

          if 0 < len(tags_rm):
            for t in tags_rm:
              # db.session.delete(t)
              p.tags.remove(t)
          
          p.tags.append(Tags.by_name(category_, create = True))

    else:
      # create
      
      price = data.get('price', None)
      
      p = Products(
        name          = data.get('name', None),
        price         = price,
        stock         = data.get('stock', None),
        stockType     = data.get('stockType', None),
        onSale        = data.get('onSale', None),
        description   = data.get('description', None),
        price_history = [],
        user = g.user, 
        tags = [Tags.by_name(category_, create = True)] if None != category_ else [])
      
      # add provided price to history if any
      if 0 < price:
        p.price_history_add(price)
      
      db.session.add(p)
    
    db.session.commit()

  except:
    pass

  else:
    if None != p.id:
      # emit updated
      io.emit(f'{IOEVENT_PRODUCTS_CHANGE_SINGLE_prefix}{p.id}')
      io.emit(f'{IOEVENT_PRODUCTS_CHANGE_prefix}{p.user.id}')
      io.emit(IOEVENT_PRODUCTS_CHANGE)
  
  return SchemaSerializeProductsTimes().dump(p)
