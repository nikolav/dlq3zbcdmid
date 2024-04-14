from flask_app import db

from models.users import Users

from config.graphql.init import query

from schemas.serialization import SchemaSerializeUsersTimes


@query.field('users')
def resolve_users(_obj, _info):

  try:
    users = db.session.scalars(
      db.select(Users)
    )
    return SchemaSerializeUsersTimes(many = True).dump(users)

  except:
    pass

  return []
