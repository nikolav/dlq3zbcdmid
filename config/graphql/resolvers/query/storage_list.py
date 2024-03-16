from flask import g

from config.graphql.init import query
from models.docs         import Docs
from config              import TAG_STORAGE


@query.field('storageList')
def resolve_storageList(obj, info):
  ls = []
  for doc in Docs.tagged(f'{TAG_STORAGE}{g.user.id}'):
    d = { name: value for name, value in doc.data.items() }
    d.update({
      'id'         : doc.id, 
      'created_at' : str(doc.created_at),
      'updated_at' : str(doc.updated_at)
    })
    ls.append(d)
  
  return ls
