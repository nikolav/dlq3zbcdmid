import os
# import json
import re
from datetime import datetime
from datetime import timezone
from typing import List
from typing import Optional

from sqlalchemy     import JSON
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from . import db
from . import productsTable
from . import usersTable
from . import ln_products_tags
from . import ln_orders_products
from src.mixins import MixinTimestamps
from src.mixins import MixinIncludesTags

PRODUCT_CATEGORY_prefix = os.getenv('PRODUCT_CATEGORY_prefix')


class Products(MixinTimestamps, MixinIncludesTags, db.Model):
  __tablename__ = productsTable
  
  id: Mapped[int] = mapped_column(primary_key = True)

  name          : Mapped[str]
  price         : Mapped[Optional[float]]
  description   : Mapped[Optional[str]]
  stockType     : Mapped[Optional[str]]
  stock         : Mapped[Optional[float]]
  onSale        : Mapped[Optional[bool]]
  user_id = mapped_column(db.ForeignKey(f'{usersTable}.id'))
  # { date: Date; price: number }[]
  price_history : Mapped[List[dict]] = mapped_column(JSON)
  
  # virtual
  user   : Mapped['Users']        = relationship(back_populates = 'products')
  docs   : Mapped[List['Docs']]   = relationship(back_populates = 'product')
  tags   : Mapped[List['Tags']]   = relationship(secondary = ln_products_tags, back_populates = 'products')
  orders : Mapped[List['Orders']] = relationship(secondary = ln_orders_products, back_populates = 'products')

  # magic
  def __repr__(self):
    return f'Products(id={self.id!r}, name={self.name!r}, user_id={self.user_id!r})'

  # public
  def price_by_date(self, d):
    # calc price by date from .price_history record
    pass
  
  # public
  def price_by_order(self, o):
    # calc price by order date from .price_history record
    pass
  
  def price_history_add(self, price):
    # doesnt commit; cache data outside
    ls = self.price_history.copy()
    ls.append({
      'day'   : datetime.now(tz = timezone.utc).isoformat(),
      'price' : price
    })
    self.price_history = ls
  
  # product price for given order
  #  taking into account .price_history record[]
  def price_for_order(self, o):
    # assumes product belongs to provided order
    price = None
    hlen  = len(self.price_history)

    if not 1 < hlen:
      # no price updates
      price = self.price
    else:
      for index in range(hlen):
        # if next price update is after order day
        #  take current node
        if index < hlen - 1:
          if o.created_at.timestamp() < datetime.fromisoformat(self.price_history[index + 1]['day']).timestamp():
            # next price update is newer than order date;
            #  take this nodes price
            price = self.price_history[index]['price']
            break
        else:
          # at last node
          price = self.price
          break
  
    return price
  
  def categories(self):
    return [t.tag for t in self.tags if t.tag.startswith(PRODUCT_CATEGORY_prefix)]
  
  def district(self):
    p = self.user.profile()
    return p.get('district', '') if p else ''
  
  def is_from_district(self, district = ''):
    return bool(re.match( f'.*{re.escape(district)}.*', 
      self.district(), flags = re.IGNORECASE))
