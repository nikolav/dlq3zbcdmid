import os
import json
import re
from pprint import pprint
from datetime import datetime
from datetime import timezone
from random import randint
from functools import reduce

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
from sqlalchemy import asc


from schemas.serialization import SchemaSerializeOrdersTimes
from schemas.serialization import SchemaSerializeProductsTimes
from schemas.serialization import SchemaSerializeDocJsonTimes

from sqlalchemy import text

from utils.str import match_after_last_colon


POST_IMAGES_prefix         = os.getenv('POST_IMAGES_prefix')
PRODUCT_CATEGORY_prefix    = os.getenv('PRODUCT_CATEGORY_prefix')
PRODUCTS_SEARCH_RANDOM_MAX = int(os.getenv('PRODUCTS_SEARCH_RANDOM_MAX'))



# SORT_METHODS_ALLOWED_db     = [1,2,5,6]
# SORT_METHODS_ALLOWED_manual = [3,4,7]




@bp_testing.route('/', methods = ('POST',))
# @arguments_schema(SchemaTesting())
def testing_home():    
  # counts grouped by districk
  district_coms_counts = {}
  tcom = Tags.by_name(os.getenv('POLICY_COMPANY'))  
  for com in tcom.users:
    d = com.profile()['district']
    if not d in district_coms_counts:
      district_coms_counts[d] = 1
    else:
      district_coms_counts[d] += 1
  
  return district_coms_counts
