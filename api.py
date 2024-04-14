import os

from flask_app import app
from flask_app import api
from flask_app import db
from flask_app import io
from flask_app import PRODUCTION
from flask_app import REBUILD_SCHEMA

from resources.docs          import DocsResource
from blueprints              import bp_home
from blueprints.auth         import bp_auth
from blueprints.storage      import bp_storage
from blueprints.testing      import bp_testing
from middleware.authenticate import authenticate


# mount resources
api.add_resource(DocsResource, '/docs/<string:tag_name>')

# @blueprints:mount
#   /auth
app.register_blueprint(bp_auth)
#   /
app.register_blueprint(bp_home)
#   /storage
app.register_blueprint(bp_storage)
#   /test
if not PRODUCTION:
  app.register_blueprint(bp_testing)


# init graphql endpoint, `POST /graphql`
import config.graphql.init


# # mount static documentation
# @app.route('/demo')
# def page_demo():
#   return render_template('index.html', time = datetime.now())

# # ..and resources
# @app.route('/<path:path>')
# def page_demo_resource(path):
#   return send_from_directory('templates', path)


# authentication.middleware@init
@app.before_request
def before_request_authenticate():
  return authenticate()

# io status check
@io.on('connect')
def io_connected():
  print('@io/connection')


if __name__ == '__main__':

  with app.app_context():
    # @app:init

    # load models
    from models.tags     import Tags
    from models.tokens   import Tokens
    from models.users    import Users
    from models.products import Products
    from models.orders   import Orders
    from models.docs     import Docs
    
    # drop/create schema
    if REBUILD_SCHEMA:
      db.drop_all()
    
    # create schema
    db.create_all()

    # init db
    import config.init_tables
    
  _port = os.getenv('PORT')
  io.run(app, 
        debug = True,
        host  = '0.0.0.0',
        port  = _port if None != _port else 5000,
        allow_unsafe_werkzeug = True)
