from config.graphql.init import query
from models.docs         import Docs
from config              import TAG_VARS


@query.field('vars')
def resolve_vars(obj, info):
  res = []
  for doc in Docs.tagged(TAG_VARS):
    for name, value in doc.data.items():
      res.append({ 'id': doc.id, 'name': name, 'value': value })
  return res
