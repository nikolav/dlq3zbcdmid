import os
# import json
# import re
from typing import List

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from . import db
from . import usersTable
from . import postsTable
from . import ln_posts_tags
from src.mixins import MixinTimestamps
from src.mixins import MixinIncludesTags

from models.tags import Tags
from models.docs import Docs
from utils.str   import match_after_last_colon

POST_IMAGES_prefix = os.getenv('POST_IMAGES_prefix')


class Posts(MixinTimestamps, MixinIncludesTags, db.Model):
  __tablename__ = postsTable
  
  id: Mapped[int] = mapped_column(primary_key = True)

  title   : Mapped[str]
  content : Mapped[str]
  user_id = mapped_column(db.ForeignKey(f'{usersTable}.id'))
  
  # virtual
  user : Mapped['Users']      = relationship(back_populates = 'posts')
  tags : Mapped[List['Tags']] = relationship(secondary = ln_posts_tags, back_populates = 'posts')
  docs : Mapped[List['Docs']] = relationship(back_populates = 'post')

  # magic
  def __repr__(self):
    return f'Posts(id={self.id!r}, title={self.title!r}, user_id={self.user_id!r})'
  
  # public
  def drop_images(self):
    tags = db.session.scalars(
            db.select(Tags)
              .where(
                Tags.tag.like(
                  f'{POST_IMAGES_prefix}{self.id}:%')))
    
    for t in tags:
      id = match_after_last_colon(t.tag)
      fd = db.session.get(Docs, id)
      if None != fd:
        path = fd.data.get("path", "")
        if os.path.exists(path):
          os.unlink(path)
        db.session.delete(fd)
      db.session.delete(t)
    db.session.commit()
