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
  tags        = fields.List(fields.String())

class SchemaSerializeUsersTimes(SchemaSerializeTimes):
  id       = fields.Integer()
  email    = fields.String()
  password = fields.String()

class SchemaSerializeOrdersTimes(SchemaSerializeTimes):
  user_id     = fields.Integer(dump_default = None)
  id          = fields.Integer()
  code        = fields.String()
  description = fields.String()
  completed   = fields.Boolean()
  canceled    = fields.Boolean()

class SchemaSerializePosts(SchemaSerializeTimes):
  id       = fields.Integer()
  title    = fields.String()
  content  = fields.String()
