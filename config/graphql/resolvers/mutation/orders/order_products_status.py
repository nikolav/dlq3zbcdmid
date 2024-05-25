import os

from sqlalchemy import update

from flask_app import db
from flask_app import io

from models.products import Products
from models.orders   import Orders
from models          import ln_orders_products

from config.graphql.init import mutation

IOEVENT_ORDER_PRODUCTS_STATUS = os.getenv('IOEVENT_ORDER_PRODUCTS_STATUS')


@mutation.field('orderProductsStatusByCompany')
def resolve_orderProductsStatusByCompany(_o, _i, oid, uid, status):
  try:
    # select pids of this user
    lsp_subq = db.select(Products.id).join(Products.orders).where(
        Orders.id        == oid,
        Products.user_id == uid
      ).subquery()
    
    upd = update(
      ln_orders_products
    ).values(
      status = status
    ).where(
      ln_orders_products.c.order_id == oid,
      ln_orders_products.c.product_id.in_(lsp_subq)
    )

    db.session.execute(upd)
    db.session.commit()


  except Exception as err:
    raise err

  else:
    io.emit(f'{IOEVENT_ORDER_PRODUCTS_STATUS}{oid}')
    return str(status)
  
  return None
