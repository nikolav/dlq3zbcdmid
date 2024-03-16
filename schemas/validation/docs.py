from marshmallow import Schema
from marshmallow import EXCLUDE
from marshmallow import fields
from marshmallow.exceptions import ValidationError as MVError


class SchemaDocs(Schema):

  class Meta:
    unknown = EXCLUDE
  
  id   = fields.Integer(required = True)
  data = fields.Dict(required = True)

