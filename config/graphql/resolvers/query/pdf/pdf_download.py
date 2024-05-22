import base64

from flask import render_template

from babel.numbers import format_currency
from babel.dates   import format_date

from flask_app         import db
from models.users      import Users
from models.orders     import Orders
from src.services.pdf  import printHtmlToPDF

from config.graphql.init import query


def render_template_order_items(data):  
  oid  = int(data.get('oid'))
  uid  = int(data.get('uid'))
  
  com         = db.session.get(Users,  uid)
  com_profile = com.profile()
  
  order       = db.session.get(Orders, oid)
  user        = order.user
  total       = order.total_original_for_company(com)
  order_items = Orders.order_products_with_amount_and_original_price_by_user(order, com)
  profile     = user.profile()
  full_name   = ' '.join(map(
    lambda d: d.capitalize(),
    (
      profile.get('firstName', '') or profile.get('ownerFirstName', ''), 
      profile.get('lastName', '')  or profile.get('ownerLastName', '')
    )
  ))

  return render_template('pdf/order-items.html', 
                         com                 = com, 
                         com_profile         = com_profile,
                         
                         user      = user,
                         profile   = profile,
                         full_name = full_name,
                         
                         order          = order,
                         date_formated  = format_date(order.created_at, locale = 'sr_RS'),
                         total          = total,
                         total_formated = format_currency(total, 'RSD', locale = 'sr_RS'),
                         
                         order_items = order_items,
                         count       = len(order_items),
                        )

TEMPLATE = {
  'order-items': render_template_order_items,
}


@query.field('pdfDownload')
def resolve_pdfDownload(_obj, _info, data):
  # file = BytesIO(printHtmlToPDF(document_from_request_data_to_render()))
  # return send_file(file,
  #   as_attachment = True,
  #   download_name = 'download.pdf',
  #   mimetype      = 'application/pdf',
  # )

  template_name = data.get('template')
  file = printHtmlToPDF(TEMPLATE[template_name](data))
  return base64.b64encode(file).decode('utf-8')

