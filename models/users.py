import os
# import json
# import re
from typing import List

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from . import db
from . import usersTable
from . import ln_users_tags
from src.mixins import MixinTimestamps
from src.mixins import MixinIncludesTags


class Users(MixinTimestamps, MixinIncludesTags, db.Model):
  __tablename__ = usersTable
  
  id: Mapped[int] = mapped_column(primary_key = True)
  
  email   : Mapped[str] = mapped_column(unique = True)
  password: Mapped[str]
  
  # virtual
  tags    : Mapped[List['Tags']]     = relationship(secondary = ln_users_tags, back_populates = 'users')
  products: Mapped[List['Products']] = relationship(back_populates = 'user')
  orders  : Mapped[List['Orders']]   = relationship(back_populates = 'user')


  # magic
  def __repr__(self):
    return f'Users(id={self.id!r}, email={self.email!r}, password={self.password!r})'
  
  
  # public
  def is_company(self):
    return self.includes_tags(os.getenv('POLICY_COMPANY'))
  
  