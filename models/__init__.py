import os

from flask_app import db


tblSuffix = os.getenv('TABLE_NAME_SUFFIX')

tagsTable     = f'tags{tblSuffix}'
usersTable    = f'users{tblSuffix}'
productsTable = f'products{tblSuffix}'
docsTable     = f'docs{tblSuffix}'

lnTableUsersTags     = f'ln_users_tags{tblSuffix}'
lnTableProductsTags  = f'ln_products_tags{tblSuffix}'
lnTableDocsTags      = f'ln_docs_tags{tblSuffix}'

# link tables, *:*
ln_users_tags = db.Table(
  lnTableUsersTags,
  db.Column('user_id', db.ForeignKey(f'{usersTable}.id'), primary_key = True),
  db.Column('tag_id',  db.ForeignKey(f'{tagsTable}.id'),  primary_key = True),
)

ln_products_tags = db.Table(
  lnTableProductsTags,
  db.Column('product_id', db.ForeignKey(f'{productsTable}.id'), primary_key = True),
  db.Column('tag_id',     db.ForeignKey(f'{tagsTable}.id'),     primary_key = True),
)

ln_docs_tags = db.Table(
  lnTableDocsTags,
  db.Column('doc_id', db.ForeignKey(f'{docsTable}.id'), primary_key = True),
  db.Column('tag_id', db.ForeignKey(f'{tagsTable}.id'), primary_key = True),
)
