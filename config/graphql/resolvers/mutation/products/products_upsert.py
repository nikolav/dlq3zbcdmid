import os
from datetime import datetime
from datetime import timezone

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

FIELDS = [
  'name',
  # 'category',
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

    if None != p:
      # update
      
      # skip forbidden updates
      if not p.user.id == g.user.id:
        raise Exception('forbidden')
      
      for field in FIELDS:
        # if 'category' != field:
        if field in data:
          if 'price' == field:
            priceNew = data['price']
            # if cache empty or doesnt match update
            if not len(p.price_history) or (priceNew != p.price_history[-1]['price']):
              if 0 <= priceNew:
                p.price_history_add({ 
                  'day'  : datetime.now(tz = timezone.utc).isoformat(), 
                  'price': priceNew })
          setattr(p, field, data[field])
    
    else:
      # create
      
      category_ = data.get('category', None)
      
      p = Products(
        name          = data.get('name', None),
        price         = data.get('price', None),
        stock         = data.get('stock', None),
        stockType     = data.get('stockType', None),
        onSale        = data.get('onSale', None),
        description   = data.get('description', None),
        price_history = [],
        user = g.user, 
        tags = [Tags.by_name(category_, create = True)] if None != category_ else [])
      
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
