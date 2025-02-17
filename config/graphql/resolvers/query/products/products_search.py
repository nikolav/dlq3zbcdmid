import os
import re

from datetime import datetime

from sqlalchemy import func
from sqlalchemy import or_

from flask_app import db

from models.tags     import Tags
from models.products import Products

from config.graphql.init import query

from schemas.serialization import SchemaSerializeProductsTimes


PRODUCTS_SEARCH_RANDOM_MAX = os.getenv('PRODUCTS_SEARCH_RANDOM_MAX')
SORT_METHODS_ALLOWED       = [1,2,3,4,5,6,7,8]
SORT_METHOD_db = {
  1: Products.price.asc(),
  2: Products.price.desc(),
  5: Products.created_at.desc(),
  6: Products.created_at.asc(),
}
SORT_METHOD_manual = {
  
  # 🌟 -rating DESC
  3: lambda ls: sorted(ls, 
                       key     = lambda p: p.rating(), 
                       reverse = True),
                       
  # 👍🏻 -likes.coun DESC
  4: lambda ls: sorted(ls, 
                       key     = lambda p: p.likes_count(), 
                       reverse = True),
                       
  # 💬 -comments.count DESC
  7: lambda ls: sorted(ls, 
                       key     = lambda p: p.comments_count(), 
                       reverse = True),
                       
  # 🏆 -total amount ordred DESC
  #   the most sales 
  8: lambda ls: sorted(ls, 
                       key     = lambda p: p.total_amount_ordered(), 
                       reverse = True)
}

@query.field('productsSearch')
def resolve_productsSearch(_obj, _info, query = None):
  # query: JSON | None
  # {
  #   'category' : '@product:category:brasno'[]
  #   'district' : 'Srem',
  #   'priceMax' : 1122,
  #   'sortBy'   : 3,
  #   'text'     : '12'
  #   'limit'    : 10
  #   'random'   : true
  # 
  #   'date_after'  : Date:isostring
  #   'date_before' : Date:isostring
  # }
  

  if not query:
    # no parameters
    return []
  
  # if True == RANDOM:
  #   return SchemaSerializeProductsTimes(many = True).dump(
  #     db.session.scalars(
  #       db.select(Products)
  #         .order_by(func.random())
  #         .limit(LIMIT or PRODUCTS_SEARCH_RANDOM_MAX)
  #     )
  #   )
  
  # lsrandom
  RANDOM       = True == query.get('random', None)

  # limit max
  limit_       = query.get('limit', None)
  LIMIT        = int(limit_) if limit_ else None

  # :string
  category     = query.get('category', None)

  # flag text search
  is_text_q    = True == query.get('isText', False)

  # # :string
  text         = query.get('text', None)
  TEXT         = text.strip().upper() if text else None

  # # :int
  d_price_max  = query.get('priceMax', None)
  PRICE        = int(d_price_max) if d_price_max else None

  # # :string
  district_    = query.get('district', None)
  district     = district_.strip() if district_ else None

  # :date-string
  date_after   = query.get('date_after', None)
  date_before  = query.get('date_before', None)

  # # 0 < :int
  sort_method_ = query.get('sortBy', None)
  sort_method  = int(sort_method_) if sort_method_ else None
  
  
  # # query --builder
  q = db.select(Products)

  # if category:
  #   q = q.join(Products.tags).where(Tags.tag == category)
  if not is_text_q:
    if category and (0 < len(category)):
      q = q.join(Products.tags).where(Tags.tag.in_(category))

  # match .name, .description, category
  if TEXT:
    q = q.where(
      or_(
        func.upper(Products.name).like(f'%{TEXT}%'),
        func.upper(Products.description).like(f'%{TEXT}%'),
        Products.tags.any(

          # postgres
          func.upper(Tags.tag).op('~')(f'.*{re.escape(TEXT)}.*') if not is_text_q else Tags.tag.in_(category)

          # sqlite
          # func.upper(Tags.tag).op('REGEXP')(f'.*{re.escape(TEXT)}.*')
          
        )
      )
    )
      
  
  if PRICE and 0 < PRICE:
    q = q.where(
      Products.price <= int(PRICE)
    )
  
  # # sort strategy
  if RANDOM:
    q = q.order_by(func.random())
  else:
    if sort_method in SORT_METHOD_db:
      # db
      #   1: .price      ASC
      #   2: .price      DESC
      #   5: .created_at DESC
      #   6: .created_at ASC    
      q = q.order_by(SORT_METHOD_db[sort_method])

  # # execute
  pls = db.session.scalars(q)

  # # manual filter/sort

  # filter on user:profle:district
  if district:
    pls = [p for p in pls if p.is_from_district(district)]
  
  # filter on [date_after < created_at]
  if None != date_after:
    d_a = datetime.fromisoformat(date_after)
    pls = [p for p in pls if d_a <= p.created_at]

  # filter on [created_at < date_before]
  if None != date_before:
    d_b = datetime.fromisoformat(date_before)
    pls = [p for p in pls if p.created_at <= d_b]

  # sort social
  if sort_method in SORT_METHOD_manual:
    pls = SORT_METHOD_manual[sort_method](pls)
  
  if LIMIT and 0 < LIMIT:
    pls = list(pls)[0:LIMIT]

  return SchemaSerializeProductsTimes(many = True).dump(pls)

