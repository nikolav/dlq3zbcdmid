import os

from marshmallow import Schema
from marshmallow import validate
from marshmallow import fields
from marshmallow import INCLUDE


AUTH_PASSWORD_MIN_LENGTH = int(os.getenv('AUTH_PASSWORD_MIN_LENGTH'))

class SchemaAuthLogin(Schema):
  email    = fields.Email(required = True)
  password = fields.Str(required = True)

class SchemaAuthRegister(Schema):
  email    = fields.Email(required = True)
  password = fields.Str(required = True, 
                        validate = validate.Length(min = AUTH_PASSWORD_MIN_LENGTH))
  company = fields.Boolean(load_default = False)

class SchemaAuthSocial(Schema):

  class Meta:
    unknown = INCLUDE
  
  email       = fields.Email(required = True)
  uid         = fields.Str()
  displayName = fields.Str()
  photoURL    = fields.Str()
