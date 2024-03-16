import os

from models.tags         import Tags
from config.graphql.init import query

from schemas.serialization import SchemaSerializeUsersTimes


@query.field('companiesList')
def resolve_companiesList(_obj, _info, approved = False):
  try:
    tag_com = Tags.by_name(os.getenv('POLICY_COMPANY_APPROVED' if approved else 'POLICY_COMPANY'))
    return SchemaSerializeUsersTimes(many = True).dump(tag_com.users)

  except:
    pass

  return []

