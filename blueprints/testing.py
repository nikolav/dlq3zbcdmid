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

from schemas.serialization import SchemaSerializeDocJsonTimes  as DocPlain
from schemas.serialization import SchemaSerializeProductsTimes as SchemaProducts
from schemas.serialization import SchemaSerializeUsersTimes    as UsersPlain

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

from flask_mail import Message
from flask_app import mail

from utils import id_gen

# class SchemaTesting(Schema):

#   class Meta:
#     unknown = EXCLUDE
    
#   x0 = fields.Integer(load_default = -9999)

from flask import render_template

@bp_testing.route('/', methods = ('POST',))
# @arguments_schema(SchemaTesting())
def testing_home():
  email_status = { 'status': None, 'error': None }

  message = Message(
    'kantar:test --html-poruka',
    sender = ("KANTAR.RS", "app@kantar.rs"),
    recipients = [
      "admin@nikolav.rs",
      # "slavko.savic@me.com",
    ]
  )
  # message.body='hello'
  message.html = render_template("mail/status.html", 
                                 status = 'ok', 
                                 link   = 'http://70.34.223.252:3001/')
  # message.html = render_template("mail/simple.html", text = f'your pin code is: { id_gen() }')
  
  try:
    mail.send(message)
  except Exception as err:
    email_status['error'] = str(err)
    print(err)
  else:
    email_status['status'] = 'ok'
  
  return email_status
