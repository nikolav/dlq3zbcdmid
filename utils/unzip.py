import gzip

def unzip(hexData):

  error    = None
  res      = None
  unzipped = None
  
  try:
    unzipped = gzip.decompress(bytes.fromhex(hexData)).decode()
  except Exception as _error:
    error = _error
  else:
    res = unzipped
  
  return error, res
