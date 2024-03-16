from functools import wraps

from flask import g
from flask import abort
from flask import make_response


def authguard(*policies):
  def with_authguard(fn_route):
    @wraps(fn_route)
    def wrapper(*args, **kwargs):
      if not g.user.includes_tags(*policies):
        return abort(make_response('', 403))
      return fn_route(*args, **kwargs)
    return wrapper
  return with_authguard
