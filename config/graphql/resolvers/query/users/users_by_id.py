from sqlalchemy.orm import joinedload

from flask_app             import db
from models.users          import Users
from config.graphql.init   import query
from schemas.serialization import SchemaSerializeUsersTimes


@query.field('usersById')
def resolve_usersById(_obj, _info, uid):
  return SchemaSerializeUsersTimes().dump(
    db.session.scalar(
      db.select(Users)
        # load joined products
        .options(joinedload(Users.products))
        .where(Users.id == uid)
    )
  )
