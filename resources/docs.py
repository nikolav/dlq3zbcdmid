import os
import json

from flask         import g
from flask_restful import Resource

from flask_app   import db
from flask_app   import io
from models.docs import Docs
from models.tags import Tags

from middleware.arguments    import arguments_schema
from schemas.validation.docs import SchemaDocs


IOEVENT_DOCS_CHANGE = os.getenv('IOEVENT_DOCS_CHANGE')

class DocsResource(Resource):

  def get(self, tag_name):
    return Docs.dicts(Docs.tagged(tag_name))
  
  
  @arguments_schema(SchemaDocs(partial = ('id',)))
  def post(self, tag_name):
    ID   = g.arguments.get('id')
    data = g.arguments['data']

    doc       = None
    doc_      = None
    docUpdate = None
    ioevent   = IOEVENT_DOCS_CHANGE
    sNewData  = ''
    status    = 200
    error     = '@error/internal.500'

    tag = Tags.by_name(tag_name, create = True)


    if ID:
      for d in tag.docs:
        if ID == d.id:
          docUpdate = d
          break

    if docUpdate:
      sOldData       = json.dumps(docUpdate.data)
      sNewData       = json.dumps(data)
      docUpdate.data = data

      if sOldData == sNewData:
        ioevent = None
      
      doc_ = docUpdate

    else:
      doc_ = Docs(id = ID, data = data)
      tag.docs.append(doc_)
      status = 201
    
    try:
      db.session.commit()
      
    except Exception as err:
      error  = err
      status = 500
      
    else:
      doc = doc_
      if ioevent:
        # change:docs:orders@122, doc{}
        # ! io_send(f'{ioevent}:{tag.tag}')
        io.emit(f'{ioevent}:{tag.tag}')
    
    return doc.dump() if doc else { 'error': str(error) }, status
  
  
  @arguments_schema(SchemaDocs(only = ('id',)))
  def delete(self, tag_name):
    ID = g.arguments['id']

    doc    = None
    tag    = None
    error  = ''
    status = 200

    tag = Tags.by_name(tag_name)


    if tag:
      for d in tag.docs:
        if ID == d.id:

          try:
            tag.docs.remove(d)
            db.session.delete(d)
            db.session.commit()

          except Exception as err:
            error  = err
            status = 500
            
          else:
            doc = d
            io.emit(f'{IOEVENT_DOCS_CHANGE}:{tag.tag}')            
          
          break
    
    return doc.dump() if doc else { 'error': str(error) }, status
