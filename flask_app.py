import os

from dotenv           import load_dotenv
from flask            import Flask
from flask_restful    import Api
from flask_cors       import CORS
from flask_sqlalchemy import SQLAlchemy
# from flask_talisman   import Talisman
# https://github.com/miguelgrinberg/flask-socketio/issues/40#issuecomment-48268526
from flask_socketio import SocketIO

from src.classes import Base as DbModelBaseClass


load_dotenv()

APP_NAME     = os.getenv('APP_NAME')
PRODUCTION   = bool(os.getenv('PRODUCTION'))
DATABASE_URI = os.getenv('DATABASE_URI_production') if PRODUCTION else os.getenv('DATABASE_URI_dev')

IO_CORS_ALLOW_ORIGINS = (
  os.getenv('IOCORS_ALLOW_ORIGIN_dev'),
  os.getenv('IOCORS_ALLOW_ORIGIN_dev_1'),
  os.getenv('IOCORS_ALLOW_ORIGIN_production'),
  os.getenv('IOCORS_ALLOW_ORIGIN_nikolavrs'),
)

REBUILD_SCHEMA_ = bool(os.getenv('REBUILD_SCHEMA'))
REBUILD_SCHEMA  = (not PRODUCTION) and REBUILD_SCHEMA_

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = not PRODUCTION

# talisman = Talisman(app, force_https = False)
cors     = CORS(app, supports_credentials = True)
api      = Api(app)
db       = SQLAlchemy(app, model_class = DbModelBaseClass)
io       = SocketIO(app, 
              cors_allowed_origins = IO_CORS_ALLOW_ORIGINS, 
              cors_supports_credentials = True)

