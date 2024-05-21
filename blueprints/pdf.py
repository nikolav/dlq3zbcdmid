# import os
from io import BytesIO
import locale

# from datetime import datetime
# from datetime import timezone

from babel.numbers import format_currency

# from flask       import g
# from flask       import Blueprint
from flask       import request
from flask       import send_file
from flask       import render_template
# from flask_cors  import CORS

from flask_app   import db
# from flask_app   import io
from flask_app   import app

from models.users    import Users
from models.orders   import Orders
# from models.tags import Tags
# from models.docs import Docs

from src.services.pdf import printHtmlToPDF


# # router config
# bp_pdf = Blueprint('pdf', __name__, url_prefix = '/pdf')
# # cors blueprints as wel for cross-domain requests
# CORS(bp_pdf)


def render_template_order_items(data):
  locale.setlocale(locale.LC_TIME, 'sr_RS.UTF-8')
  
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
    (profile.get('firstName', ''), profile.get('lastName', ''))
  ))

  return render_template('pdf/order-items.html', 
                         com                 = com, 
                         com_profile         = com_profile,
                         
                         user      = user,
                         profile   = profile,
                         full_name = full_name,
                         
                         order          = order,
                         date_formated  = order.created_at.strftime('%d. %B, %Y.'),
                         total          = total,
                         total_formated = format_currency(total, 'RSD', locale = 'sr_RS'),
                         
                         order_items = order_items,
                         count       = len(order_items),
                         )


TEMPLATE = {
  'order-items': render_template_order_items,
}


@app.route('/pdf', methods = ('POST',))
# @authguard(os.getenv('POLICY_FILESTORAGE'))
def pdf_download():
  data          = request.get_json()
  template_name = data.get('template')
    
  # file = BytesIO(printHtmlToPDF(document_from_request_data_to_render()))
  file = BytesIO(printHtmlToPDF(TEMPLATE[template_name](data)))

  return send_file(file,
    as_attachment = True,
    download_name = 'download.pdf',
    mimetype      = 'application/pdf',
  )
