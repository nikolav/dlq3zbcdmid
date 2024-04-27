import os

from flask import g

from flask_app import db
from flask_app import io

from models.posts          import Posts
from config.graphql.init   import mutation
from schemas.serialization import SchemaSerializePosts
from middleware.authguard  import authguard_company_approved
# from middleware.authguard import authguard

IOEVENT_POST_CHANGE_SINGLE_prefix = os.getenv('IOEVENT_POST_CHANGE_SINGLE_prefix')
IOEVENT_USER_POSTS_CHANGE_prefix  = os.getenv('IOEVENT_USER_POSTS_CHANGE_prefix')
IOEVENT_POSTS_CHANGE              = os.getenv('IOEVENT_POSTS_CHANGE')

# input InputPost {
#   title: String
#   content: String
# }

POSTS_KEYS_UPDATE_WHITELIST = [
  "title", 
  "content",
]

@mutation.field('postsUpsert')
@authguard_company_approved
def resolve_postsUpsert(_obj, _info, data, id = None):
  p = None
  
  try:
    p = db.session.get(Posts, id) if None != id else None

    if None != p:
      # update
      
      # skip forbidden; edit owned posts only
      if not p.user.id == g.user.id:
        raise Exception('forbidden --owned-only')
      
      for field in POSTS_KEYS_UPDATE_WHITELIST:
        if field in data:
          setattr(p, field, data[field])
    
    else:
      # create
      
      #  @todo
      # keywords = data.get('keywords', None)

      p = Posts(
        
        #  default to blank title/content
        title   = data.get('title',   ''),
        content = data.get('content', ''),
        user    = g.user, 
        
        #  @todo --attachments
        # tags    = [Tags.by_name(category_, create = True)] if None != category_ else []
        # docs    = [Docs(data = { 'keyword': kw }) for kw in keywords]
      )
      
      db.session.add(p)
    
    db.session.commit()

  except:
    pass
    # raise err

  else:
    if None != p.id:
      # @io --posts-updated
      io.emit(f'{IOEVENT_POST_CHANGE_SINGLE_prefix}{p.id}')
      io.emit(f'{IOEVENT_USER_POSTS_CHANGE_prefix}{p.user.id}')
      io.emit(IOEVENT_POSTS_CHANGE)
  
  return SchemaSerializePosts().dump(p)
