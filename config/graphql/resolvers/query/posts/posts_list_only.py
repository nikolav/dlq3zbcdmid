

from config.graphql.init import query
from flask_app import db
from models.posts import Posts
from schemas.serialization import SchemaSerializePosts

@query.field('postsListOnly')
def resolve_postsListOnly(_o, _i, sids):
  
  try:
    posts = db.session.scalars(
      db.select(Posts)
        .where(Posts.id.in_(sids))
    )
    return SchemaSerializePosts(many = True).dump(posts)

  except Exception as err:
    raise err
  
  return []

