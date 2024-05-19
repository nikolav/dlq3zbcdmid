import os

from flask_app import db
from flask_app import io

from models.products     import Products

from config.graphql.init import mutation

IOEVENT_PACKAGES_PROMOTED_prefix = os.getenv('IOEVENT_PACKAGES_PROMOTED_prefix')


@mutation.field('packagesSetPromoted')
def resolve_packagesSetPromoted(_obj, _info, pid, status = True):
  updated = False

  try:
    p       = db.session.get(Products, pid)
    updated = p.packages_set_promoted(status) if p else False

  except Exception as err:
    raise err
    # pass
    
  else:
    if updated:
      # emit change
      io.emit(f'{IOEVENT_PACKAGES_PROMOTED_prefix}{pid}')
      return pid
  
  return None
