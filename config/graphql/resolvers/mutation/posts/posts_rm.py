import os

from flask     import g
from flask_app import db
from flask_app import io

from models.posts          import Posts
from models.docs           import Docs
from models.tags           import Tags
from config.graphql.init   import mutation
from schemas.serialization import SchemaSerializePosts

from middleware.authguard import authguard_company_approved
# from middleware.authguard import authguard

# IOEVENT_POST_CHANGE_SINGLE_prefix = os.getenv('IOEVENT_POST_CHANGE_SINGLE_prefix')
IOEVENT_USER_POSTS_CHANGE_prefix  = os.getenv('IOEVENT_USER_POSTS_CHANGE_prefix')
# IOEVENT_POSTS_CHANGE              = os.getenv('IOEVENT_POSTS_CHANGE')


# garbadge collects related doc-images when post is removed
# rm from `docs` where tag like `{POST_IMAGES_prefix}{postId}:`
POST_IMAGES_prefix = os.getenv('POST_IMAGES_prefix')


from utils.str import match_after_last_colon


@mutation.field('postsRemove')
@authguard_company_approved
def resolve_postsRemove(_obj, _info, id):
  p   = None
  uid = None

  try:
    p = db.session.get(Posts, id)

    # @forbidden raise
    if not p:
      raise Exception('forbidden')
    
    if not p.user.id == g.user.id:
      raise Exception('forbidden')
    
    # cache uid for io.emit
    #  `p.user` .user unavailable after post.delete
    uid = p.user.id
    
    # approved company
    # remove owned product record
    g.user.posts.remove(p)
    db.session.delete(p)
    
    db.session.commit()

  except Exception as err:
    # raise err
    pass

  else:

    if None != p.id:
      
      # post removed here, garbage collect related nodes
      #  check related attachments, images, docs, to remove
      #   then rm Tags related

      # 1.images
      tags = db.session.scalars(
              db.select(Tags)
                .where(
                  Tags.tag.like(
                    f'{POST_IMAGES_prefix}{p.id}:%')))
      for t in tags:
        id = match_after_last_colon(t.tag)
        fd = db.session.get(Docs, id)
        path = fd.data.get("path", "")
        if os.path.exists(path):
          os.unlink(path)
        db.session.delete(t)
        db.session.delete(fd)
      db.session.commit()
      
      
      # get related file-docs to remove
      #  rm where tag like '{POST_IMAGES_prefix}{ppid}%'
      
      # @todo remove related docs-attachments    
    
    
    if None != p.id:
      # # emit updated
      # io.emit(f'{IOEVENT_POST_CHANGE_SINGLE_prefix}{p.id}')
      io.emit(f'{IOEVENT_USER_POSTS_CHANGE_prefix}{uid}')
      # io.emit(IOEVENT_POSTS_CHANGE)
  
  return SchemaSerializePosts().dump(p) if None != p else None
