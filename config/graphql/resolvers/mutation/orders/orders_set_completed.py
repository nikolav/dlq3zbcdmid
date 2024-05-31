import os

from flask      import render_template
from flask_mail import Message

from flask_app           import io
from flask_app           import db
from flask_app           import mail

from models.orders       import Orders
from models.users        import Users
from config.graphql.init import mutation


# IOEVENT_ORDERS_CHANGE = os.getenv('IOEVENT_ORDERS_CHANGE')
IOEVENT_ORDER_UPDATED             = os.getenv('IOEVENT_ORDER_UPDATED')
ORDER_COMPLETED_FEEDBACK_FORM_URL = os.getenv('ORDER_COMPLETED_FEEDBACK_FORM_URL')


@mutation.field('ordersSetCompleted')
def r_ordersSetCompleted(_o, _i, oid, completed = None):
  flag_initial = None
  
  try:
    o = db.session.get(Orders, oid)
    
    if not o:
      raise Exception('--r_ordersSetCompleted')
    
    flag_initial = o.completed
    
    o.completed = bool(completed)
    db.session.commit()

  except Exception as err:
    raise err
  
  else:
    if o.completed != flag_initial:
      io.emit(f'{IOEVENT_ORDER_UPDATED}{oid}')
    
    if o.completed and not o.feedback_on_completed_sent():
      o.feedback_on_completed_sent_set()
      try:
        u = db.session.get(Users, o.user_id)
        mail.send(
          Message(
            
            # subject
            f'narudzba-realizovana:[#{o.id}]@kantar.rs',

            # from
            sender = ('KANTAR.RS', 'app@kantar.rs'),
            
            # default recepiens ls
            recipients = [u.email],

            # pass all data to mail template
            html = render_template(f'mail/feedback-order-completed.html', 
                                   order             = o, 
                                   feedback_form_url = ORDER_COMPLETED_FEEDBACK_FORM_URL)
          )
        )
      
      except Exception as err:
        raise err
    
    return str(oid)
  
  return None
