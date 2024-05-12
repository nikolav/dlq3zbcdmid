import os

from config.graphql.init import query
from models.tags         import Tags

from schemas.serialization import SchemaSerializeUsersTimes


@query.field('companiesList')
def resolve_companiesList(_obj, _info, approved = False, district = None):
  ls_com = []

  t_coms = Tags.by_name(os.getenv('POLICY_COMPANY'))
  coms   = t_coms.users if None == district else [com for com in t_coms.users if district == com.profile()['district']]
  
  sch = SchemaSerializeUsersTimes(exclude = ('password', 'products',))
  for com in coms:
    lsp  = com.products_sorted_popular()
    node = sch.dump(com)
    node['products'] = lsp
    ls_com.append(node)

  return ls_com
