from flask import g

from config.graphql.init import query
from config              import fields_profile_complete


@query.field('accountsIncompleteProfileFields')
def resolve_accountsIncompleteProfileFields(_o, _i):
  blank = []
  
  try:
    p = g.user.profile()
    for field, value in p.items():
      if not value:
        if field in fields_profile_complete:
          blank.append(field)
        
  except Exception as err:
    raise err

  else:
    return blank
  
  return []
