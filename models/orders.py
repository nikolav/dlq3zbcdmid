# import os
# import json
# import re
from typing import List
from typing import Optional

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from . import db
from . import ordersTable
from . import usersTable
from . import ln_orders_products
from . import ln_orders_tags
from src.mixins import MixinTimestamps
from src.mixins import MixinIncludesTags


class Orders(MixinTimestamps, MixinIncludesTags, db.Model):
  __tablename__ = ordersTable
  
  id: Mapped[int] = mapped_column(primary_key = True)

  code        : Mapped[Optional[str]]
  description : Mapped[Optional[str]]
  completed   : Mapped[Optional[bool]]
  canceled    : Mapped[Optional[bool]]
  user_id = mapped_column(db.ForeignKey(f'{usersTable}.id'))
  
  # virtual
  tags     : Mapped[List['Tags']]     = relationship(secondary = ln_orders_tags, back_populates = 'orders')
  user     : Mapped['Users']          = relationship(back_populates = 'orders')
  products : Mapped[List['Products']] = relationship(secondary = ln_orders_products, back_populates = 'orders')
  
  
  # magic
  def __repr__(self):
    return f'Orders(id={self.id!r}, user_id={self.user_id!r})'

