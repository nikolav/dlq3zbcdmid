import re

r_last_segment_after_colon = '^.*?:?([^:]*)$'

def last_segment_after_colon(value):
  try:
    return re.match(r_last_segment_after_colon, value).group(1)
  except:
    pass
  
  return ""

print(last_segment_after_colon("a:b::c"))