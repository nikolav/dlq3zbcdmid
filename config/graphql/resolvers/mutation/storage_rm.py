import os

from flask import g

from flask_app import db
from flask_app import io

from middleware.authguard import authguard
from config.graphql.init  import mutation
from models.tags          import Tags
from config               import TAG_STORAGE

from utils.doc_json_date import docJsonDates as doc_plain


@mutation.field('storageRemoveFile')
@authguard(os.getenv('POLICY_FILESTORAGE'))
def resolve_storageRemoveFile(_obj, _info, file_id):
  print(f'remove: file_id [{file_id}]')
  # try
  #  file exists
  #   unlink
  #    rm data @db
  #     @200, file deleted, io:change
  error        = ''
  doc_file     = None
  tag_storage_ = f'{TAG_STORAGE}{g.user.id}'


  try:
    # get related file Docs{}
    tag = Tags.by_name(f'{TAG_STORAGE}{g.user.id}', create = True)
    for doc in tag.docs:
      if file_id == doc.data['file_id']:
        doc_file = doc
        break
    
    if not doc_file:
      raise Exception('file not found')
    
    if not os.path.exists(doc_file.data['path']):
      raise Exception('no file')
    
  except Exception as err:
    error = err
    
  else:
    
    try:
      os.unlink(doc_file.data['path'])
      
    except Exception as err:
      error = err
    
    else:
      if not os.path.exists(doc_file.data['path']):
        try:
          tag.docs.remove(doc_file)
          db.session.delete(doc_file)
          db.session.commit()
          
        except Exception as err:
          error = err

        else:
          # @200, file deleted
          io.emit(tag_storage_)
          return { 'error': None, 'file': doc_plain(doc_file) }
  
  return { 'error': str(error), 'file': None }
