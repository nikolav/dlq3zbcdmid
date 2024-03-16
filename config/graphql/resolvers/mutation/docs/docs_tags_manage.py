from flask_app import db
from flask_app import io

from models.tags import Tags
from models.docs import Docs

from config.graphql.init import mutation
from . import IOEVENT_DOCS_TAGS_CHANGE_prefix

@mutation.field('docsTags')
def resolve_docsTags(_obj, _info, id, tags):
  res = {}
  doc = None
  modified = False

  try:
    doc = db.session.get(Docs, id)
    if None != doc:
      for key, value in tags.items():
        if isinstance(value, bool):
          if value:
            # add tag
            tag_ = Tags.by_name(key, create = True)
            if not tag_ in doc.tags:
              doc.tags.append(tag_)
              modified = True
          else:
            # remove tag
            tag_ = Tags.by_name(key)
            if (None != tag_) and (tag_ in doc.tags):
              doc.tags.remove(tag_)
              modified = True
          
          res[key] = value
          
  except Exception as error:
    print(error)
    
  else:
    db.session.commit()
    if modified:
      io.emit(f'{IOEVENT_DOCS_TAGS_CHANGE_prefix}{doc.id}')
  
  return res
