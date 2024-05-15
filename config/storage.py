
# @storage:allow-all
# ALLOWED_EXTENSIONS = {'*', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'md'}

# @storage:allow-images
ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png', 'gif', 'svg', 'webp', 'bmp', 'tiff', 'tif'}

RE_EXT = r'^.*\.([^\.]+)$'
