from functools import wraps
from pprint    import pprint

from flask import request
from flask import g
from flask import abort
from flask import make_response

from marshmallow.exceptions import ValidationError as MVError


def arguments_schema(schema_validate):
  def arguments_schema_validate(fnView):
    @wraps(fnView)
    def wrapper(*args, **kwargs):
      error  = '@error/internal.500'
      status = 500

      try:
        # validate/load request data
        arguments = schema_validate.load(request.get_json())

      except MVError as err:
        # @400
        error  = err
        status = 400

      except Exception as err:
        # @500
        error = err
      
      else:
        # @200
        # set global `.arguments` to parsed input; run next
        g.arguments = arguments
        return fnView(*args, **kwargs)
      
      # abort, send error
      pprint(error, indent = 2)
      return abort(make_response({ 'error': str(error) }, status))
    return wrapper
  return arguments_schema_validate
