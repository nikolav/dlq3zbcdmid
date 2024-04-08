PATHS_SKIP_AUTH = (
  
  # status check
  r'^/$',
  
  # auth.allow
  r'^/auth/register$',
  r'^/auth/login$',
  
  # storage.allow-download
  r'^/storage/[0-9a-fA-F]+$',
)

TAG_VARS         = '@vars'
TAG_IS_FILE      = '@isfile'
TAG_STORAGE      = '@storage:'


init_docs_tags = (TAG_VARS, TAG_IS_FILE)


KEY_TOKEN_CREATED_AT = '@'

DEFAULT_POPULAR_PRODUCTS_LIMIT = 10
