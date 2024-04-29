import os
import json
from pprint import pprint

from flask      import Blueprint
from flask      import request
from flask      import g
from flask_cors import CORS
from flask_cors import cross_origin
from flask      import make_response
from flask      import abort

from sqlalchemy.orm import joinedload

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


POST_IMAGES_prefix = os.getenv('POST_IMAGES_prefix')

from utils.str import match_after_last_colon

@bp_testing.route('/', methods = ('POST',))
# @arguments_schema(SchemaTesting())
def testing_home():
  # return list([t.tag for t in db.session.scalars(
  #   db.select(Tags)
  # )])
  tags = db.session.scalars(
            db.select(Tags)
              .where(Tags.tag.like(f'{POST_IMAGES_prefix}{2}:%')))

  images = map(lambda id: db.session.get(Docs, id), 
          [match_after_last_colon(t.tag) for t in tags])

  return SchemaSerializeDocJsonTimes(many = True).dump(images)
  