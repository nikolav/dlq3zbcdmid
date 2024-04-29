import os

from flask_app import db

from models.tags  import Tags
from models.docs  import Docs
from config.graphql.init import query

from schemas.serialization import SchemaSerializeDocJsonTimes

from utils.str import match_after_last_colon

POST_IMAGES_prefix = os.getenv('POST_IMAGES_prefix')

@query.field('postsImages')
def resolve_postsImages(_obj, _info, id):

  if not id:
    return None
    
  tags = db.session.scalars(
            db.select(Tags)
              .where(Tags.tag.like(f'{POST_IMAGES_prefix}{id}:%')))

  images = map(lambda id: db.session.get(Docs, id), 
          [match_after_last_colon(t.tag) for t in tags])

  return SchemaSerializeDocJsonTimes(many = True).dump(images)
