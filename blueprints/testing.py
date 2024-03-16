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

from sqlalchemy import select
from sqlalchemy import literal_column
from sqlalchemy import text
from sqlalchemy import func

from flask_app       import db
from flask_app       import app
from models.tags     import Tags
from models.docs     import Docs
# from utils.pw       import hash  as hashPassword
# from utils.pw       import check as checkPassword
# from utils.jwtToken import issueToken
# from utils.jwtToken import setInvalid as tokenSetInvalid
# from config         import TAG_USERS

from middleware.authguard import authguard

bp_testing = Blueprint('testing', __name__, url_prefix = '/test')

# cors blueprints as wel for cross-domain requests
cors_bp_testing = CORS(bp_testing)

from schemas.serialization   import SchemaSerializeDocJsonTimes  as DocPlain
from schemas.serialization   import SchemaSerializeProductsTimes as SchemaProducts

from marshmallow.exceptions  import ValidationError
from marshmallow  import Schema
from marshmallow  import fields
from marshmallow  import EXCLUDE

from middleware.arguments import arguments_schema

from models.tags      import Tags
from models.tokens    import Tokens
from models.users     import Users
from models.products  import Products
from models.docs      import Docs

class SchemaTesting(Schema):

  class Meta:
    unknown = EXCLUDE
    
  x0 = fields.Integer(load_default = -9999)

@bp_testing.route('/', methods = ('POST',))
@arguments_schema(SchemaTesting())
def testing_home():
  print(f'--testing: ')
  print(g.user)

  # for i in range(20):
  #   p = Products(name = f'p:{i}')
  #   db.session.add(p)

  # db.session.commit()
  
  # t = Tags.by_name('@products:category:foo1', create = True)
  # p = db.session.get(Products, 10)
  # t.products.append(p)
  # # t.users.append(u)
  # db.session.commit()
  # p = db.session.get(Products, 4)
  u = db.session.get(Users, 4)
  
  # u.products.append(p)
  # db.session.commit()

  return { 'res': SchemaProducts(many = True).dump(u.products) }
  # return { 'res': 'ok' }

