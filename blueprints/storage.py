import os

from flask       import Blueprint
from flask       import g
from flask       import send_file
from flask_cors  import CORS

from flask_app   import db
from flask_app   import io
from models.tags import Tags
from models.docs import Docs

from middleware.wrappers.files import files
from middleware.authguard      import authguard
# from middleware.arguments      import arguments_schema

from schemas.validation.storage import SchemaStorageFile

from utils import id_gen
from utils import gen_filename
from utils.mimetype      import mimetype
from utils.doc_json_date import docJsonDates as doc_plain

from config import TAG_STORAGE
from config import TAG_IS_FILE


UPLOAD_PATH   = os.getenv('UPLOAD_PATH')
UPLOAD_DIR    = os.getenv('UPLOAD_DIR')

# router config
bp_storage = Blueprint('storage', __name__, url_prefix = '/storage')

# cors blueprints as wel for cross-domain requests
CORS(bp_storage)

@bp_storage.route('/', methods = ('POST',))
# @authguard(os.getenv('POLICY_FILESTORAGE'))
@files
def storage_upload():
  saved  = {}
  status = 400
  tag_storage_ = f'{TAG_STORAGE}{g.user.id}'

  for name, node in g.files.items():
    # try:
    #   save file locally
    #    dump file_data from schema
    #     persist file_data @Docs
    #      @success: 201, signal io:changed
    file_id_  = id_gen()
    filename_ = gen_filename(node['file'].filename, file_id_)
    filepath_ = os.path.join(os.path.abspath(UPLOAD_PATH), UPLOAD_DIR, str(g.user.id), filename_)

    try:

      # ensure path exists
      try:
        os.makedirs(os.path.dirname(filepath_))

      except:
        pass
      
      # save file
      node['file'].save(filepath_)
      
    except:
      pass
    
    else:
      if os.path.exists(filepath_):
        file_data = {
            'file_id'  : file_id_,
            'user_id'  : g.user.id,
            'filename' : filename_,
            'path'     : filepath_,
            'size'     : os.path.getsize(filepath_),
            'mimetype' : mimetype(node['file']),
          }
        # assign fields @.data { title, description }
        #  can require `title` and `description` from users
        #   (..supply additional data on nodes to app users)
        file_data.update(node['data'])
        
        try:
          file_data = SchemaStorageFile().load(file_data)
          
        except:
          pass
        
        else:

          # persist
          try:
            
            doc_file_data = Docs(data = file_data)
            
            tag = Tags.by_name(tag_storage_, create = True)
            tag_isfile = Tags.by_name(TAG_IS_FILE, create = True)
            
            # link file tags
            tag.docs.append(doc_file_data)
            tag_isfile.docs.append(doc_file_data)

            db.session.commit()
            
          except:
            pass
          
          else:

            # @201; file uploaded, data cached
            saved[name] = doc_plain(doc_file_data)
            
            # provide `node.emits` field at clients
            #  send on demand signals to clients
            if 'emits' in node['meta']:
              io.emit(node['meta']['emits'])

  
  if 0 < len(saved):
    status = 201
    # signal updates
    io.emit(tag_storage_)
  
  return saved, status


# @bp_storage.route('/', methods = ('DELETE',))
# @authguard(os.getenv('POLICY_FILESTORAGE'))
# @arguments_schema(SchemaStorageRemoveArguments())
# def storage_remove():
#   # try
#   #  file exists
#   #   unlink
#   #    rm data @db
#   #     @200, file deleted, io:change

#   error    = ''
#   status   = 400
#   doc_file = None
#   tag_storage_ = f'{TAG_STORAGE}{g.user.id}'


#   try:
#     # get related file Docs{}
#     tag = Tags.by_name(f'{TAG_STORAGE}{g.user.id}', create = True)
#     for doc in tag.docs:
#       if g.arguments['file_id'] == doc.data['file_id']:
#         doc_file = doc
#         break
    
#     if not doc_file:
#       raise Exception('file not found')
    
#     if not os.path.exists(doc_file.data['path']):
#       raise Exception('no file')
    
#   except Exception as err:
#     error = err
    
#   else:
    
#     try:
#       os.unlink(doc_file.data['path'])
      
#     except Exception as err:
#       error  = err
#       status = 500
    
#     else:
#       if not os.path.exists(doc_file.data['path']):
#         try:
#           tag.docs.remove(doc_file)
#           db.session.delete(doc_file)
#           db.session.commit()
          
#         except Exception as err:
#           error  = err
#           status = 500

#         else:
#           # @200, file deleted
#           io.emit(tag_storage_)
#           return doc_plain(doc_file), 200
  
#   return { 'error': str(error) }, status


@bp_storage.route('/<string:file_id>', methods = ('GET',))
def storage_download(file_id):
  
  error  = ''
  status = 400

  doc_dl_file = None
  

  try:

    tag_isfile = Tags.by_name(TAG_IS_FILE, create = True)

    for doc in tag_isfile.docs:
      if file_id == doc.data['file_id']:
        doc_dl_file = doc
        break
      
    if not doc_dl_file:
      raise Exception('file not found')
    
    if not os.path.exists(doc_dl_file.data['path']):
      raise Exception('no file')
    
    if not doc_dl_file.data['public']:
      status = 403
      raise Exception('access denied')
    
    
  except Exception as err:
    error = err
  
  else:
      return send_file(doc_dl_file.data['path'], 
                      as_attachment = True)
  
  return { 'error': str(error) }, status
  

# @Docs/file
#   .file_id
#   .user_id
#   .title
#   .description
#   .filename
#   .path
#   .size
#   .mimetype
#   .public

# 'close', 'content_length', 'content_type', 'filename', 
# 'headers', 'mimetype', 'mimetype_params', 'name'
