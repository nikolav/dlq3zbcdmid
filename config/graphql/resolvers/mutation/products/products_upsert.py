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

IOEVENT_PRODUCTS_CHANGE_prefix = os.getenv('IOEVENT_PRODUCTS_CHANGE_prefix')

FIELDS = [
  'name',
  'category',
  'price',
  'stock',
  'stockType',
  'onSale',
  'description',
]

# input InputProduct {
#   name: String!
#   category: String!
#   price: Number
#   stockType: String
#   stock: Number
#   onSale: Boolean
#   description: String
# }

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
        if 'category' != field:
          if field in data:
            setattr(p, field, data[field])
    
    else:
      # create
      
      category_ = data.get('category', None)
      
      p = Products(
        name        = data.get('name', None),
        price       = data.get('price', None),
        stock       = data.get('stock', None),
        stockType   = data.get('stockType', None),
        onSale      = data.get('onSale', None),
        description = data.get('description', None),
        user = g.user, 
        tags = [Tags.by_name(category_, create = True)] if None != category_ else [])
      
      db.session.add(p)
    
    db.session.commit()

  except:
    pass

  else:
    if None != p.id:
      # emit updated
      io.emit(f'{IOEVENT_PRODUCTS_CHANGE_prefix}{g.user.id}')
  
  return SchemaSerializeProductsTimes().dump(p)
