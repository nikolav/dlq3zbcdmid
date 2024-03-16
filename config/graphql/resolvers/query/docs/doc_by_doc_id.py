from models.docs import Docs
from config.graphql.init import query


@query.field('docByDocId')
def resolve_docByDocId(_obj, _info, doc_id):
  return Docs.by_doc_id(doc_id, create = True).dump()
