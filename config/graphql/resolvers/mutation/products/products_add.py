from flask_app import db

from models.users import Users
from models.tags  import Tags
from models.products import Products
from config.graphql.init import mutation
from schemas.serialization import SchemaSerializeProductsTimes


@mutation.field('productsAdd')
def resolve_productsAdd(_obj, _info, name, user_id, tags = []):
  # docUpsert(doc_id: String!, data: JsonData!): JsonData!
  user = None

  try:
    user = db.session.get(Users, user_id)

    if not user:
      raise Exception('unavailable.com')

    if not user.is_company():
      raise Exception('unavailable.com')
      
    
    p = Products(name = name, 
                 user = user, 
                 tags = [Tags.by_name(t, create = True) for t in tags]
                 )
    db.session.add(p)

    db.session.commit()

  except:
    pass

  else:
    if None != p.id:
      return SchemaSerializeProductsTimes().dump(p)
    # emit updated
    # io.emit(f'{IOEVENT_DOC_CHANGE_prefix}{doc_id}')
  
  return None
