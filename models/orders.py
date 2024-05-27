# import os
# import json
# import re
from datetime import datetime

from typing import List
from typing import Optional

from flask import g

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

from models.products import Products

from schemas.serialization import SchemaSerializeProductsTimes


ORDER_STATUS = {
  '1': 'narudžbenica primljena',
  '2': 'priprema robe',
  '3': 'spremno',
  '4': 'pošta pošiljka #',
}


class Orders(MixinTimestamps, MixinIncludesTags, db.Model):
  __tablename__ = ordersTable
  
  id: Mapped[int] = mapped_column(primary_key = True)

  code        : Mapped[Optional[str]]
  description : Mapped[Optional[str]]
  completed   : Mapped[Optional[bool]]
  canceled    : Mapped[Optional[bool]]
  status      : Mapped[Optional[int]]
  delivery_at : Mapped[Optional[datetime]]
  user_id = mapped_column(db.ForeignKey(f'{usersTable}.id'))
  
  # virtual
  tags     : Mapped[List['Tags']]     = relationship(secondary = ln_orders_tags, back_populates = 'orders')
  user     : Mapped['Users']          = relationship(back_populates = 'orders')
  products : Mapped[List['Products']] = relationship(secondary = ln_orders_products, back_populates = 'orders')
  docs     : Mapped[List['Docs']]     = relationship(back_populates = 'order')
  
  
  # magic
  def __repr__(self):
    return f'Orders(id={self.id!r}, user_id={self.user_id!r})'
  
  def products_with_amount(self):
    return db.session.execute(
      db.select(Products, ln_orders_products.c.amount)
        .join(ln_orders_products)
        .join(Orders)
        .where(Orders.id == self.id))

  def products_with_amount_for_company(self, user):
    return db.session.execute(
      db.select(Products, ln_orders_products.c.amount)
        .join(ln_orders_products)
        .join(Orders)
        .where(
          Orders.id        == self.id,
          Products.user_id == user.id
        ))
  
  # calc original total for all items
  def total_original(self):
    tot = 0
    for p, amount in self.products_with_amount():
      tot += amount * p.price_for_order(self)
    return tot

  # calc original total for products@user
  def total_original_for_company(self, user):
    tot = 0
    for p, amount in self.products_with_amount_for_company(user):
      tot += amount * p.price_for_order(self)
    return tot
  
  @staticmethod
  def order_products_with_amount_and_original_price_by_user(order, user):
    ls = []
    for p, amount in order.products_with_amount_for_company(user):
      node = SchemaSerializeProductsTimes().dump(p)
      node.update({ 
        'amount'          : int(amount),
        'price_original'  : int(p.price_for_order(order)),
      })
      ls.append(node)
    
    return ls
