import os

from dotenv           import load_dotenv
from flask            import Flask
from flask_restful    import Api
from flask_cors       import CORS
from flask_sqlalchemy import SQLAlchemy
# from flask_talisman   import Talisman
# https://github.com/miguelgrinberg/flask-socketio/issues/40#issuecomment-48268526
from flask_socketio import SocketIO
# https://pythonhosted.org/Flask-Mail/
from flask_mail import Mail

from src.classes import Base as DbModelBaseClass


load_dotenv()

APP_NAME     = os.getenv('APP_NAME')
PRODUCTION   = bool(os.getenv('PRODUCTION'))
DATABASE_URI = os.getenv('DATABASE_URI_production') if PRODUCTION else os.getenv('DATABASE_URI_dev')

IO_CORS_ALLOW_ORIGINS = (
  os.getenv('IOCORS_ALLOW_ORIGIN_dev'),
  os.getenv('IOCORS_ALLOW_ORIGIN_dev_1'),
  os.getenv('IOCORS_ALLOW_ORIGIN_dev_2'),
  os.getenv('IOCORS_ALLOW_ORIGIN_nikolavrs'),
  os.getenv('IOCORS_ALLOW_ORIGIN_production'),
  os.getenv('IOCORS_ALLOW_ORIGIN_production_2'),
)

REBUILD_SCHEMA_ = bool(os.getenv('REBUILD_SCHEMA'))
REBUILD_SCHEMA  = (not PRODUCTION) and REBUILD_SCHEMA_

app = Flask(__name__)

# app-config
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# app-config:db
app.config['SQLALCHEMY_DATABASE_URI']        = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO']                = not PRODUCTION

# app-config:email
app.config['MAIL_SERVER']            = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT']              = os.getenv('MAIL_PORT')
app.config['MAIL_USERNAME']          = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD']          = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS']           = bool(os.getenv('MAIL_USE_TLS'))
app.config['MAIL_USE_SSL']           = bool(os.getenv('MAIL_USE_SSL'))
app.config['MAIL_ASCII_ATTACHMENTS'] = bool(os.getenv('MAIL_ASCII_ATTACHMENTS'))


# talisman = Talisman(app, force_https = False)
cors  = CORS(app, supports_credentials = True)
api   = Api(app)
db    = SQLAlchemy(app, model_class = DbModelBaseClass)
io    = SocketIO(app, 
                 cors_allowed_origins = IO_CORS_ALLOW_ORIGINS, 
                 cors_supports_credentials = True)
mail  = Mail(app)

