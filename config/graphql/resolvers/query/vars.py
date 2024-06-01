from config.graphql.init import query
from models.docs         import Docs
from config              import TAG_VARS


@query.field('vars')
def resolve_vars(_o, _i):
  return Docs.vars_list()
