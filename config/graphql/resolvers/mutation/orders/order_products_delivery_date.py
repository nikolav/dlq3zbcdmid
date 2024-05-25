import os
from datetime import datetime

from sqlalchemy import update

from flask_app import db
from flask_app import io

from config.graphql.init import mutation
from models import ln_orders_products
from models.products import Products
from models.orders import Orders

IOEVENT_ORDER_PRODUCTS_DELIVERY_AT = os.getenv('IOEVENT_ORDER_PRODUCTS_DELIVERY_AT')


@mutation.field('orderProductsDeliveryDateByCompany')
def resolve_orderProductsDeliveryDateByCompany(_o, _i, oid, uid, date):
  try:
    dd = datetime.fromisoformat(date)
    db.session.execute(
      update(ln_orders_products)
      .values(
        delivery_at = dd
      )
      .where(
        ln_orders_products.c.order_id == oid,
        ln_orders_products.c.product_id.in_(
          db.select(Products.id)
            .join(Products.orders)
            .where(
              Orders.id        == oid,
              Products.user_id == uid
            )
            .subquery()
        )
      )
    )
    db.session.commit()

  except Exception as err:
    raise err
    
  else:
    io.emit(f'{IOEVENT_ORDER_PRODUCTS_DELIVERY_AT}{oid}')
    return str(oid)

  return None
