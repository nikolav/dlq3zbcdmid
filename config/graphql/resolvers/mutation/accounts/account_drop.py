from flask import g

from flask_app import db

from models          import ln_orders_products
from models          import ln_users_tags
from models          import ln_products_tags
from models.users    import Users
from models.orders   import Orders
from models.products import Products
from models.posts    import Posts
from models.docs     import Docs

from config.graphql.init import mutation
from utils.jwtToken import setInvalid as token_set_invalid


@mutation.field('accountsDrop')
def resollve_accountsDrop(_o, _i, uid):
  
  try:
    u = db.session.get(Users, uid)
    
    if not u.id == g.user.id:
      raise Exception('access denied')
    
    uid = u.id

    subq_oids = db.select(Orders.id).where(Orders.user_id == uid).subquery()
    subq_pids = db.select(Products.id).where(Products.user_id == uid).subquery()
    
    db.session.execute(
      db.delete(ln_orders_products)
        .where(ln_orders_products.c.order_id.in_(subq_oids))
    ) 
    db.session.execute(
    db.delete(Orders)
      .where(
        Orders.user_id == uid
      )
    )

    db.session.execute(
      db.delete(ln_products_tags)
        .where(ln_products_tags.c.product_id.in_(subq_pids))
    ) 
    db.session.execute(
      db.delete(ln_orders_products)
        .where(ln_orders_products.c.product_id.in_(subq_pids))
    ) 
    db.session.execute(
      db.delete(Products)
      .where(
        Products.user_id == uid
      )
    )
    
    db.session.execute(
      db.delete(ln_users_tags)
        .where(ln_users_tags.c.user_id == uid)
    )
    
    db.session.execute(
      db.delete(Posts)
        .where(
          Posts.user_id == uid
        )
    )
    
    db.session.execute(
      db.delete(Docs)
        .where(
          Docs.user_id == uid
        )
    )
    
    db.session.execute(
      db.delete(Users)
        .where(
          Users.id == uid
        )
    )
    
    db.session.commit()
    Users.clear_storage(uid)
    token_set_invalid(g.access_token)
    
  except Exception as err:
    raise err

  else:
    return uid
  
  return None
