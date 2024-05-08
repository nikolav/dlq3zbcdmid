import os

from flask      import g
from sqlalchemy import update

from flask_app import db
from flask_app import io

from models.products     import Products
from models.orders       import Orders
from models              import ln_orders_products

from config.graphql.init import mutation

from flask      import render_template
from flask_mail import Message
from flask_app  import mail


# IOEVENT_PRODUCTS_CHANGE_prefix = os.getenv('IOEVENT_PRODUCTS_CHANGE_prefix')
# IOEVENT_PRODUCTS_CHANGE        = os.getenv('IOEVENT_PRODUCTS_CHANGE')
IOEVENT_ORDERS_CHANGE          = os.getenv('IOEVENT_ORDERS_CHANGE')
MAIL_COMPANIES_ON_ORDER        = bool(os.getenv('MAIL_COMPANIES_ON_ORDER'))

@mutation.field('ordersPlace')
def resolve_ordersPlace(_obj, _info, data, items):
  # .items Record<id:number, amount:number>
  # .data Record<name:string, value:any>
  
  com        = []
  uids       = set()
  o          = None
  orderd_ids = items.keys()

  try:
    
    # products:ordered
    lsProductsOrdered = [p for p in db.session.scalars(
      db.select(Products)
        .where(
          Products.id.in_(orderd_ids), 
          # skip own products
          Products.user_id != g.user.id
        )
    )]
    
    if not 0 < len(lsProductsOrdered):
      raise Exception('--ordersPlace-skip-cRXgtZgd7Z')

    # insert order
    o = Orders(
      code        = data.get('code', ''),
      description = data.get('description', ''),
      user        = g.user,
      products    = lsProductsOrdered
      )
    db.session.add(o)
    db.session.commit()

    for p in lsProductsOrdered:
      # cache statement to run
      #  store order-products amounts
      db.session.execute(      
        update(ln_orders_products).values(amount = items.get(str(p.id))).where(
          ln_orders_products.c.order_id   == o.id,
          ln_orders_products.c.product_id == p.id
        )
      )
      
      # add related companies
      if not p.user.id in uids:
        com.append(p.user)

      uids.add(p.user.id)
    
    db.session.commit()

  except Exception as err:
    print('--mutation-ordersPlace')
    print(err)

  else:
    # notify companies
    for company in com:
      # io, upadtes ui
      io.emit(f'{IOEVENT_ORDERS_CHANGE}{company.id}')
    
    # refresh user ui
    io.emit(f'{IOEVENT_ORDERS_CHANGE}{g.user.id}')

    if MAIL_COMPANIES_ON_ORDER:
      try:
        # send mail to related companies
        print(f'sending mails to companies')
        mail.send(
          Message(
            'nova.narudžba@kantar.rs --B.2 --user:prodavac',
            sender = ('KANTAR.RS', 'app@kantar.rs'),
            recipients = [c.email for c in com],
            # recipients = ['admin@nikolav.rs', 'slavko.savic@me.com'],
            html = render_template('mail/simple.html', text = f'nova narudzba [Ref #{o.id}] --dev')
          )
        )
      except:
        pass
    
    if True == data.get('email', None):
      try:
        # if confirmed, send mail to user who placed order
        print(f'sending mail to user')
        mail.send(
          Message(
            'nova.narudžba@kantar.rs --B.2 --user:kupac',
            sender = ('KANTAR.RS', 'app@kantar.rs'),
            # recipients = [c.email for c in com],
            # recipients = ['admin@nikolav.rs', 'slavko.savic@me.com'],
            recipients = [g.user.email],
            html = render_template('mail/simple.html', text = f'nova narudzba [Ref #{o.id}] --dev')
          )
        )
      except:
        pass

  return o.id if None != o else None
