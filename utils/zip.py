import gzip

def zip(text = ''):

  zipped = None
  res    = None
  error  = None
  
  try:
    zipped = gzip.compress(text.encode()).hex()
  except Exception as _error:
    error = _error
  else:
    res = zipped

  return error, res
