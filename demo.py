# import os
# from dotenv         import load_dotenv
# from sqlalchemy     import create_engine
# from sqlalchemy     import text
# from sqlalchemy.orm import Session


# load_dotenv()

# engine = create_engine(os.getenv('DATABASE_URI_dev'))

# with Session(engine) as session:
#   res = session.execute(text('select * from main'))
#   for r in res:
#     print(r)


from marshmallow import Schema
from marshmallow import validate
from marshmallow import fields

class Schema1(Schema):
  name = fields.String(required = True)
  company = fields.Boolean(load_default = False)

node = Schema1().load({ 'name': 'foo' })

print(node)

