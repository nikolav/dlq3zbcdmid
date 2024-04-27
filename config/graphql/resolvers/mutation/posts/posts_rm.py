# import os

from flask     import g
from flask_app import db
# from flask_app import io

from models.posts          import Posts
from config.graphql.init   import mutation
from schemas.serialization import SchemaSerializePosts

from middleware.authguard import authguard_company_approved
# from middleware.authguard import authguard

# IOEVENT_PRODUCTS_CHANGE_prefix = os.getenv('IOEVENT_PRODUCTS_CHANGE_prefix')
# IOEVENT_PRODUCTS_CHANGE        = os.getenv('IOEVENT_PRODUCTS_CHANGE')

@mutation.field('postsRemove')
@authguard_company_approved
def resolve_postsRemove(_obj, _info, id = None):
  p = None

  try:
    p = db.session.get(Posts, id)

    # @forbidden raise
    if not p:
      raise Exception('forbidden')
    if not p.user.id == g.user.id:
      raise Exception('forbidden')
    
    # approved company
    # remove owned product record
    g.user.posts.remove(p)
    db.session.delete(p)
    
    db.session.commit()

  except:
    # raise err
    pass

  else:
    if None != p.id:
      # # emit updated
      # io.emit(f'{IOEVENT_PRODUCTS_CHANGE_prefix}{g.user.id}')
      # io.emit(IOEVENT_PRODUCTS_CHANGE)
      return SchemaSerializePosts().dump(p)
  
  return None
