import json
from functools import wraps

from flask import request
from flask import abort
from flask import make_response
from flask import g

from utils.upload_allowed import upload_allowed


def files(fn_route):
  @wraps(fn_route)
  def wrapper(*args, **kwargs):
    error  = ''
    status = 200

    try:
      
      # get valid name:file dict from request
      # .files: { file01: { file: File, data: {} }, .. }
      files_valid = {}
      for name, f in request.files.items():
        if upload_allowed(f.filename if f else ''):
          files_valid[name] = {
            # File{}
            'file': f,
            # posted file data{}
            #   { 'title': 'foo', 'description': 'bar' }?
            'data': json.loads(request.form[name]) if name in request.form else {}
          }

      # abort if no files passed
      if not 0 < len(files_valid):
        raise Exception
      
    except Exception as err:
      error  = err
      status = 400
      
    else:
      # cache valid files/data @globals; run next
      g.files = files_valid
      return fn_route(*args, **kwargs)
    
    return abort(make_response({ 'error': str(error) }, status))
  return wrapper
