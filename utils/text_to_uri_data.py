import base64

def text_to_uri_data(text_data = ''):
  b64data = base64.b64encode(text_data.encode('utf-8')).decode('utf-8')
  return f'data:text/html;base64,{b64data}'
