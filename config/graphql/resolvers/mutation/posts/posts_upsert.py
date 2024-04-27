# import os

from flask import g

from flask_app import db
# from flask_app import io

# from models.tags  import Tags
from models.posts          import Posts
from config.graphql.init   import mutation
# from schemas.serialization import SchemaSerializeProductsTimes
from schemas.serialization import SchemaSerializePosts
from middleware.authguard  import authguard_company_approved
# from middleware.authguard import authguard

# IOEVENT_PRODUCTS_CHANGE_prefix = os.getenv('IOEVENT_PRODUCTS_CHANGE_prefix')
# IOEVENT_PRODUCTS_CHANGE        = os.getenv('IOEVENT_PRODUCTS_CHANGE')

# input InputPost {
#   title: String
#   content: String
# }

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
      
      for field in data:
        setattr(p, field, data[field])
    
    else:
      # create
      
      # @todo
      # keywords = data.get('keywords', None)

      p = Posts(
        title   = data.get('title',   None),
        content = data.get('content', None),
        user    = g.user, 
        # tags    = [Tags.by_name(category_, create = True)] if None != category_ else []
        # docs    = [Docs(data = { 'keyword': kw }) for kw in keywords]
      )
      
      db.session.add(p)
    
    db.session.commit()

  except Exception as err:
    raise err

  # else:
  #   if None != p.id:
  #     # emit updated
  #     io.emit(f'{IOEVENT_PRODUCTS_CHANGE_prefix}{g.user.id}')
  #     io.emit(IOEVENT_PRODUCTS_CHANGE)
  
  return SchemaSerializePosts().dump(p)
