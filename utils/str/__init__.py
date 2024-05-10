import re

r_last_segment_after_underscore = '^.*?_?([^_]*)$'
r_last_segment_after_colon      = '^.*?:?([^:]*)$'
r_last_segment_after_at         = '^.*?@?([^@]*)$'
r_story_image_id_match          = '^.*?@([^:]*):.*$'


def match_after_last_colon(value):
  try:
    return re.match(r_last_segment_after_colon, value).group(1)
  except:
    pass
  
  return ""

def match_after_last_underscore(value):
  try:
    return re.match(r_last_segment_after_underscore, value).group(1)
  except:
    pass
  
  return ""

def match_after_last_at(value):
  try:
    return re.match(r_last_segment_after_at, value).group(1)
  except:
    pass
  
  return ""

def match_story_id(value):
  try:
    return re.match(r_story_image_id_match, value).group(1)
  except:
    pass
  
  return ""
