from flask_app import db
from flask_app import io

from models.docs import Docs
from config.graphql.init import mutation
from . import IOEVENT_DOC_CHANGE_prefix


@mutation.field('docUpsert')
def resolve_docUpsert(_obj, _info, doc_id, data):
  # docUpsert(doc_id: String!, data: JsonData!): JsonData!
  doc = Docs.by_doc_id(doc_id, create = True)

  try:
    doc.data = data
    db.session.commit()

  except:
    pass

  else:
    # emit updated
    io.emit(f'{IOEVENT_DOC_CHANGE_prefix}{doc_id}')
  
  return doc.dump()
