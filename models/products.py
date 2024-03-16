# import os
# import json
# import re
from typing import List

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from . import db
from . import productsTable
from . import usersTable
from . import ln_products_tags
from src.mixins import MixinTimestamps
from src.mixins import MixinIncludesTags


class Products(MixinTimestamps, MixinIncludesTags, db.Model):
  __tablename__ = productsTable
  
  id: Mapped[int] = mapped_column(primary_key = True)
  name: Mapped[str]
  
  user_id = mapped_column(db.ForeignKey(f'{usersTable}.id'))
  
  # virtual
  tags: Mapped[List['Tags']] = relationship(secondary = ln_products_tags,
                                            back_populates = 'products')
  
  user: Mapped['Users'] = relationship(back_populates = 'products')
  
  # magic
  def __repr__(self):
    return f'Products(id={self.id!r}, name={self.name!r}, user_id={self.user_id!r})'

