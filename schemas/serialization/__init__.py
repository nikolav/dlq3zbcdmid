from marshmallow import Schema
from marshmallow import fields

class SchemaSerializeTimes(Schema):
  created_at = fields.DateTime()
  updated_at = fields.DateTime()

class SchemaSerializeDocJson(Schema):
  id   = fields.Int()
  data = fields.Dict()


class SchemaSerializeDocJsonTimes(SchemaSerializeDocJson):
  created_at = fields.DateTime()
  updated_at = fields.DateTime()

class SchemaSerializeProductsTimes(SchemaSerializeTimes):
  id          = fields.Integer()
  user_id     = fields.Integer(dump_default = None)
  name        = fields.String()
  price       = fields.Float()
  description = fields.String()
  stockType   = fields.String()
  stock       = fields.Float()
  onSale      = fields.Boolean()

class SchemaSerializeUsersTimes(SchemaSerializeTimes):
  id       = fields.Integer()
  email    = fields.String()
  password = fields.String()
