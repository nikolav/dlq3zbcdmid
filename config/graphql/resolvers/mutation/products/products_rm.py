import os

from flask import g

from flask_app import db
from flask_app import io

# from models.tags  import Tags
# from models.users import Users
from models.products import Products
from config.graphql.init import mutation
from schemas.serialization import SchemaSerializeProductsTimes
# from middleware.authguard import authguard
from middleware.authguard import authguard_company_approved

IOEVENT_PRODUCTS_CHANGE_prefix = os.getenv('IOEVENT_PRODUCTS_CHANGE_prefix')

@mutation.field('productsRm')
@authguard_company_approved
def resolve_productsRm(_obj, _info, id):
  p = None

  try:
    p = db.session.get(Products, id)

    if not p:
      raise Exception('forbidden')
      
    if not p.user.id == g.user.id:
      raise Exception('forbidden')
    
    # approved company
    # remove owned product record
    g.user.products.remove(p)
    db.session.delete(p)
    
    db.session.commit()

  except:
    pass

  else:
    if None != p.id:
      # emit updated
      io.emit(f'{IOEVENT_PRODUCTS_CHANGE_prefix}{g.user.id}')
      return SchemaSerializeProductsTimes().dump(p)
  
  return None
