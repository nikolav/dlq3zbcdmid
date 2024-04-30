import os

from flask_app import db
from flask_app import io

from models.posts          import Posts
from config.graphql.init   import mutation
from schemas.serialization import SchemaSerializePosts

IOEVENT_STORY_PHOTOS_CHANGE_prefix  = os.getenv('IOEVENT_STORY_PHOTOS_CHANGE_prefix')


@mutation.field('postsImagesDrop')
def resolve_postsImagesDrop(_obj, _info, id):
  p = None
  try:
    p = db.session.get(Posts, id)
    if None != p:
      p.drop_images()
    
  except Exception as error:
    raise error
    # pass
  else:
    if None != p:
      io.emit(f'{IOEVENT_STORY_PHOTOS_CHANGE_prefix}{p.id}')
    return SchemaSerializePosts().dump(p)
  
  return None
