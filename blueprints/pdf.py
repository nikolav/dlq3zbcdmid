# import os
from io import BytesIO

# from flask       import g
from flask       import Blueprint
from flask       import request
from flask       import send_file
from flask_cors  import CORS

# from flask_app   import db
# from flask_app   import io
# from models.tags import Tags
# from models.docs import Docs

from src.services.pdf import printHtmlToPDF


# router config
bp_pdf = Blueprint('pdf', __name__, url_prefix = '/pdf')

# cors blueprints as wel for cross-domain requests
CORS(bp_pdf)


@bp_pdf.route('/', methods = ('POST',))
# @authguard(os.getenv('POLICY_FILESTORAGE'))
def pdf_download():

  data  = request.get_json()
  name  = data.get('name')
  val   = data.get('value')
  
  def document_from_request_data_to_render_default():
    return f'{name}: [{val}]'
  
  file = BytesIO(printHtmlToPDF(document_from_request_data_to_render_default()))

  return send_file(file,
    as_attachment = True,
    download_name = 'download.pdf',
    mimetype      = 'application/pdf',
  )
