import os
import json
import re
from pprint import pprint
from datetime import datetime
from datetime import timezone
from random import randint

from flask      import Blueprint
from flask      import request
from flask      import g
from flask_cors import CORS
from flask_cors import cross_origin
from flask      import make_response
from flask      import abort

from sqlalchemy.orm import joinedload
from sqlalchemy     import or_

from flask_app       import db
from flask_app       import app
# from utils.pw       import hash  as hashPassword
# from utils.pw       import check as checkPassword
# from utils.jwtToken import issueToken
# from utils.jwtToken import setInvalid as tokenSetInvalid
# from config         import TAG_USERS

from middleware.authguard import authguard

bp_testing = Blueprint('testing', __name__, url_prefix = '/test')

# cors blueprints as wel for cross-domain requests
cors_bp_testing = CORS(bp_testing)

from schemas.serialization import SchemaSerializeDocJsonTimes  as DocPlain
from schemas.serialization import SchemaSerializeProductsTimes as SchemaProducts
from schemas.serialization import SchemaSerializeUsersTimes    as UsersPlain
from schemas.serialization import SchemaSerializePosts

from marshmallow.exceptions  import ValidationError
from marshmallow  import Schema
from marshmallow  import fields
from marshmallow  import EXCLUDE

from middleware.arguments import arguments_schema

from models.tags      import Tags
from models.tokens    import Tokens
from models.users     import Users
from models.products  import Products
from models.orders    import Orders
from models.docs      import Docs
from models.posts     import Posts
from models           import ln_orders_products

from flask_mail import Message
from flask_app  import mail

from utils import id_gen

# class SchemaTesting(Schema):

#   class Meta:
#     unknown = EXCLUDE
    
#   x0 = fields.Integer(load_default = -9999)

from flask import render_template

from sqlalchemy import func
from sqlalchemy import desc


from schemas.serialization import SchemaSerializeOrdersTimes
from schemas.serialization import SchemaSerializeProductsTimes
from schemas.serialization import SchemaSerializeDocJsonTimes

from sqlalchemy import text


POST_IMAGES_prefix      = os.getenv('POST_IMAGES_prefix')
PRODUCT_CATEGORY_prefix = os.getenv('PRODUCT_CATEGORY_prefix')


from utils.str import match_after_last_colon



@bp_testing.route('/', methods = ('POST',))
# @arguments_schema(SchemaTesting())
def testing_home():  

  # {
  # 'category' : '@product:category:brasno',
  # 'district' : 'Srem',
  # 'priceMax' : 1122,
  # 'sortBy'   : 3,
  # 'text'     : '12'
  # }

  
  data = request.get_json()
  
  if not 0 < len(data):
    # no parameters; send random
    return SchemaSerializeProductsTimes(many = True).dump(
      db.session.scalars(
        db.select(Products)
          .order_by(func.random())
          .limit(5)
      )
    )

  category     = data.get('category', None)

  text         = data.get('text', None)
  TEXT         = text.strip().upper() if text else None

  d_price_max  = data.get('priceMax', None)
  PRICE        = int(d_price_max) if d_price_max else None

  district_    = data.get('district', None)
  district     = district_.strip() if district_ else None

  q = db.select(Products)

  if category:
    q = q.join(Products.tags).where(Tags.tag == category)

  if TEXT:
    q = q.where(
      or_(
        func.upper(Products.name).like(f'%{TEXT}%'),
        func.upper(Products.description).like(f'%{TEXT}%'),
        Products.tags.any(
          # func.upper(Tags.tag).like((f'%{PRODUCT_CATEGORY_prefix}{TEXT}%').upper())
          func.upper(Tags.tag).op('~')(f'.*{re.escape(TEXT)}.*')
        )
      )
    )
  
  if PRICE:
    q = q.where(
      Products.price <= int(PRICE)
    )

  pls = db.session.scalars(q)


  if district:
    # filter on user:profle:district
    pls = [p for p in pls if p.is_from_district(district)]
  
  
  return SchemaSerializeProductsTimes(many = True).dump(pls)
  
  # return []
