import os


from flask_app import db
from flask_app import io

from models.tags import Tags
from models.docs import Docs

from config.graphql.init import mutation
from . import IOEVENT_DOCS_TAGS_CHANGE_prefix
from utils.str import match_after_last_colon
from utils.str import match_after_last_underscore

IOEVENT_PRODUCT_IMAGES_CHANGE_prefix = os.getenv('IOEVENT_PRODUCT_IMAGES_CHANGE_prefix')
PRODUCT_IMAGES_prefix = os.getenv('PRODUCT_IMAGES_prefix')

@mutation.field('docsTags')
def resolve_docsTags(_obj, _info, id, tags):
  res = {}
  doc = None

  modified = False
  
  # collect added/removed tags
  tags_managed  = []
  ioevents_product_images_managed = []

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
              tags_managed.append(key)
          else:
            # remove tag
            tag_ = Tags.by_name(key)
            if (None != tag_) and (tag_ in doc.tags):
              doc.tags.remove(tag_)
              modified = True
              tags_managed.append(key)
          
          res[key] = value
          
  except Exception as error:
    print(error)
    
  else:
    db.session.commit()

    if modified:
      io.emit(f'{IOEVENT_DOCS_TAGS_CHANGE_prefix}{doc.id}')
      
      # detect if `@product:images:{pid}`
      # filter tags_managed, @starts_with `@images:product:{pid}`; 
      #  @each io:emit {IOEVENT_PRODUCT_IMAGES_CHANGE_prefix}{pid}
      ioevents_product_images_managed = [
        f'{IOEVENT_PRODUCT_IMAGES_CHANGE_prefix}{match_after_last_colon(name)}' 
          for name in tags_managed 
            if name.startswith(PRODUCT_IMAGES_prefix)
      ]
      for ioevent_ in ioevents_product_images_managed:
        io.emit(ioevent_)

  return res
