from random import randbytes

from marshmallow import Schema
from marshmallow import fields
from marshmallow import EXCLUDE


class SchemaStorageFile(Schema):

  class Meta:
    unknown = EXCLUDE
  
  file_id     = fields.Str(load_default = lambda: randbytes(4).hex())
  user_id     = fields.Int(required = True)
  title       = fields.Str(load_default = '')
  description = fields.Str(load_default = '')
  filename    = fields.Str(required = True)
  path        = fields.Str(required = True)
  size        = fields.Int(required = True)
  mimetype    = fields.Str(load_default = 'application/octet-stream')
  public      = fields.Bool(load_default = True)


class SchemaStorageRemoveArguments(Schema):
  file_id = fields.Str(required = True)
