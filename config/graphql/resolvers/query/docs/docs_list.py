from models.tags import Tags
from models.docs import Docs
from config.graphql.init import query


@query.field('docsByTopic')
def resolve_docsByTopic(_obj, _info, topic):
  return Docs.dicts(Tags.by_name(topic, create = True).docs)

