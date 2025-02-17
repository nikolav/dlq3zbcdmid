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

def authguard_company_approved(fn_route):
  @wraps(fn_route)
  def wrapper(*args, **kwargs):
    try:
      
      if not g.user.is_company():
        raise Exception('unavailable.com')
      
      if not g.user.approved():
        raise Exception('unavailable.com')
    
    except:
      return abort(make_response('', 403))

    return fn_route(*args, **kwargs)
  
  return wrapper
