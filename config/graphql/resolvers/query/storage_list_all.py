from flask import g

from config.graphql.init import query
from models.docs         import Docs
from config              import TAG_IS_FILE


@query.field('storageListAll')
def resolve_storageListAll(obj, info):
  ls = []
  for doc in Docs.tagged(TAG_IS_FILE):
    d = { name: value for name, value in doc.data.items() }
    d.update({
      'id'         : doc.id, 
      'created_at' : str(doc.created_at),
      'updated_at' : str(doc.updated_at)
    })
    ls.append(d)
  
  return ls
