import os

from config.graphql.init import query
from models.tags         import Tags


@query.field('companiesCountedByDistrict')
def resolve_companiesCountedByDistrict(_obj, _info):
  # counts grouped by district
  district_coms_counts = {}
  tcom = Tags.by_name(os.getenv('POLICY_COMPANY'))  
  for com in tcom.users:
    d = com.profile()['district']
    if not d in district_coms_counts:
      district_coms_counts[d] = 1
    else:
      district_coms_counts[d] += 1
  
  return district_coms_counts
