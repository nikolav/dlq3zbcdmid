from flask_app import db
from models.docs import Docs
from models.tags import Tags

from models.docs import Docs
from config.graphql.init import query


@query.field('tagsByDocId')
def resolve_tagsByDocId(_obj, _info, id):
  result = None
  
  try:
    result = db.session.scalars(
      db.select(Tags).join(Tags.docs).where(
        Docs.id == id
      )
    )
    
  except:
    pass
  
  else:
    if None != result:
      return [t.tag for t in result]
  
  
  return []
