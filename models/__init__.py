import os

from sqlalchemy import Float
from sqlalchemy import Integer

from flask_app import db


POLICY_APPROVED = os.getenv('POLICY_APPROVED')

tblSuffix = os.getenv('TABLE_NAME_SUFFIX')

tagsTable     = f'tags{tblSuffix}'
usersTable    = f'users{tblSuffix}'
productsTable = f'products{tblSuffix}'
ordersTable   = f'orders{tblSuffix}'
docsTable     = f'docs{tblSuffix}'

lnTableUsersTags      = f'ln_users_tags{tblSuffix}'
lnTableProductsTags   = f'ln_products_tags{tblSuffix}'
lnTableOrdersProducts = f'ln_orders_products{tblSuffix}'
lnTableOrdersTags     = f'ln_orders_tags{tblSuffix}'
lnTableDocsTags       = f'ln_docs_tags{tblSuffix}'

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

ln_orders_products = db.Table(
  lnTableOrdersProducts,
  db.Column('order_id',   db.ForeignKey(f'{ordersTable}.id'),   primary_key = True),
  db.Column('product_id', db.ForeignKey(f'{productsTable}.id'), primary_key = True),
  db.Column('amount', Float),
)

ln_orders_tags = db.Table(
  lnTableOrdersTags,
  db.Column('order_id', db.ForeignKey(f'{ordersTable}.id'), primary_key = True),
  db.Column('tag_id',   db.ForeignKey(f'{tagsTable}.id'),   primary_key = True),
)

ln_docs_tags = db.Table(
  lnTableDocsTags,
  db.Column('doc_id', db.ForeignKey(f'{docsTable}.id'), primary_key = True),
  db.Column('tag_id', db.ForeignKey(f'{tagsTable}.id'), primary_key = True),
)
