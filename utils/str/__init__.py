import re

r_last_segment_after_colon = '^.*?:?([^:]*)$'
r_last_segment_after_underscore = '^.*?_?([^_]*)$'

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
