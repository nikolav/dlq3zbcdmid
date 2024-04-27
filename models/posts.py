# import os
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
