from config.graphql.init import query

@query.field('status')
def status(obj, info):
  return 'ok'
