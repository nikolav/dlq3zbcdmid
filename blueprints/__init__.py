import os
# import locale
# from io import BytesIO

import sqlalchemy

# from flask      import send_file
from flask      import Blueprint
from flask      import render_template
from flask      import request
from flask_cors                  import CORS
from flask_mail                  import Message
# from babel.numbers import format_currency

from config                      import TAG_VARS
from models.docs                 import Docs
# from models.orders               import Orders
from models.tags                 import Tags
from models.users                import Users
from flask_app                   import db
from flask_app                   import mail
# from middleware.wrappers.timelog import timelog
# from src.services.pdf            import printHtmlToPDF
from utils.jwtToken              import encode

ADMIN_EMAIL   = os.getenv('ADMIN_EMAIL')
USER_EMAIL    = os.getenv('USER_EMAIL')
POLICY_ADMINS = os.getenv('POLICY_ADMINS')

bp_home = Blueprint('home', __name__, url_prefix = '/')

# cors blueprints as wel for cross-domain requests
CORS(bp_home)

@bp_home.route('/', methods = ('GET',))
def status_ok():
  
  admin_email = ''
  app_name    = ''
  
  
  for d in Docs.tagged(TAG_VARS):

    if 'app:name' in d.data:
      app_name = d.data['app:name']
      
    if 'admin:email' in d.data:
      admin_email = d.data['admin:email']
    
    if app_name and admin_email:
      break

  
  uid = db.session.scalar(
    db.select(Users.id)
    .where(Users.email == USER_EMAIL)
  )
  
  uid_admin = db.session.scalar(
    db.select(Users.id)
    .where(Users.email == ADMIN_EMAIL)
  )
  
  uids_admin = [u.id for u in Tags.by_name(POLICY_ADMINS).users]

  return {
    'status'        : 'ok',
    'app:name'      : app_name,
    'admin:email'   : admin_email,
    'admin:pin'     : uid_admin,
    'uid:default'   : uid,
    'token:default' : encode({ 'id': uid }),
    'sqlalchemy'    : sqlalchemy.__version__,
    'admins'        : uids_admin,
  }

@bp_home.route('/packages-request', methods = ('POST',))
def packages_request_mail():
  # request:data
  #  .name .type .contact .message
  data = request.get_json()
  
  name         = data.get('name')
  package_type = data.get('type')
  contact      = data.get('contact')
  message      = data.get('message')

  res = mail.send(
    Message(
      f'zahtev-za-paket:{package_type}@kantar.rs',
      sender = ('KANTAR.RS', 'app@kantar.rs'),
      recipients = [
        'admin@nikolav.rs', 
        'slavko.savic@me.com',
      ],
      html = render_template(
        'mail/simple.html', 
        text = f'[{name}] \n\n[{package_type} paket] \n\n[Kontakt: {contact}] \n\n --- {message}'
      )
    )
  )

  return { 'status': 'ok' if not res else str(res) }


@bp_home.route('/sendmail-general', methods = ('POST',))
def packages_onpayment_mail():
  from config import MAIL_RECIPIENTS

  request_data = request.get_json()
  subject      = request_data.get('subject')
  template     = request_data.get('template', '').removesuffix('.html')
  data         = request_data.get('data', {})
  
  res = '--error:sendmail-general'
  
  if not template or not subject:
    raise '--error:sendmail-general --input'

  res = mail.send(
    Message(
      
      # subject
      f'{subject}@kantar.rs',

      # from
      sender = ('KANTAR.RS', 'app@kantar.rs'),
      
      # default recepiens ls
      recipients = MAIL_RECIPIENTS,

      # pass all data to mail template
      html = render_template(f'mail/{template}.html', data = data)
      
    )
  )

  return { 'status': 'ok' if not res else str(res) }


# def render_template_order_items(data):
#   locale.setlocale(locale.LC_TIME, 'sr_RS.UTF-8')
  
#   oid  = int(data.get('oid'))
#   uid  = int(data.get('uid'))
  
#   com         = db.session.get(Users,  uid)
#   com_profile = com.profile()
  
#   order       = db.session.get(Orders, oid)
#   user        = order.user
#   total       = order.total_original_for_company(com)
#   order_items = Orders.order_products_with_amount_and_original_price_by_user(order, com)
#   profile     = user.profile()
#   full_name   = ' '.join(map(
#     lambda d: d.capitalize(),
#     (profile.get('firstName', ''), profile.get('lastName', ''))
#   ))

#   return render_template('pdf/order-items.html', 
#                          com                 = com, 
#                          com_profile         = com_profile,
                         
#                          user      = user,
#                          profile   = profile,
#                          full_name = full_name,
                         
#                          order          = order,
#                          date_formated  = order.created_at.strftime('%d. %B, %Y.'),
#                          total          = total,
#                          total_formated = format_currency(total, 'RSD', locale = 'sr_RS'),
                         
#                          order_items = order_items,
#                          count       = len(order_items),
#                          )


# TEMPLATE = {
#   'order-items': render_template_order_items,
# }


# @bp_home.route('/dl', methods = ('POST',))
# def pdf_download():
#   data          = request.get_json()
#   template_name = data.get('template')
    
#   # file = BytesIO(printHtmlToPDF(document_from_request_data_to_render()))
#   file = BytesIO(printHtmlToPDF(TEMPLATE[template_name](data)))

#   return send_file(file,
#     as_attachment = True,
#     download_name = 'download.pdf',
#     mimetype      = 'application/pdf',
#   )
