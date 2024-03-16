import re

from config.storage import ALLOWED_EXTENSIONS
from config.storage import RE_EXT


def upload_allowed(filename):
  
  if '*' in ALLOWED_EXTENSIONS:
    return True
    
  m = re.match(RE_EXT, filename)
  return m.groups()[0] in ALLOWED_EXTENSIONS if m else False
