from mimetypes import MimeTypes


MIMETYPE_DEFAULT = 'application/octet-stream'

def mimetype(file):
  m = MimeTypes(strict = False)
  if isinstance(file, str):
    return m.guess_type(file)[0] or MIMETYPE_DEFAULT
  return file.mimetype or m.guess_type(file.filename)[0] or MIMETYPE_DEFAULT
