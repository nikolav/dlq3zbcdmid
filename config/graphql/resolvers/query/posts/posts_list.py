from sqlalchemy.orm import joinedload
from flask import g

from flask_app import db

from models.posts import Posts
from models.users import Users
from config.graphql.init import query


from schemas.serialization import SchemaSerializeProductsTimes
from schemas.serialization import SchemaSerializePosts


@query.field('postsList')
def resolve_postsList(_obj, _info, uid = None):
  from pprint import pprint
  
  try:
    id = uid if None != uid else g.user.id

    if None == id:
      raise Exception('--resolve_postsList unavailable')
    
    posts = db.session.scalars(
      db.select(Posts)
        .options(
          joinedload(Posts.user),
          joinedload(Posts.tags), 
          joinedload(Posts.docs) 
        )
        .where(Posts.user_id == id)
    ).unique()
    
    res = SchemaSerializePosts(many = True).dump(posts)

    pprint(res)

    return res

  except Exception as err:
    raise err
    # pass

  return []
