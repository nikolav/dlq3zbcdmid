import os
# import json
# import re
from typing import List

from sqlalchemy     import func
from sqlalchemy     import desc
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from . import db
from . import usersTable
from . import ln_users_tags
from . import POLICY_APPROVED
from src.mixins import MixinTimestamps
from src.mixins import MixinIncludesTags

from models          import ln_orders_products
from models.tags     import Tags
from models.docs     import Docs
from models.products import Products

from utils.str import match_after_last_at
from utils.pw  import hash as hashPassword

from schemas.serialization import SchemaSerializeProductsTimes


POLICY_COMPANY        = os.getenv('POLICY_COMPANY')
USER_EMAIL            = os.getenv('USER_EMAIL')
POLICY_PACKAGE_SILVER = os.getenv('POLICY_PACKAGE_SILVER')
POLICY_PACKAGE_GOLD   = os.getenv('POLICY_PACKAGE_GOLD')

PKG = {
  'silver': POLICY_PACKAGE_SILVER,
  'gold'  : POLICY_PACKAGE_GOLD,
}


class Users(MixinTimestamps, MixinIncludesTags, db.Model):
  __tablename__ = usersTable
  
  id: Mapped[int] = mapped_column(primary_key = True)
  
  email    : Mapped[str] = mapped_column(unique = True)
  password : Mapped[str]
  
  # virtual
  tags     : Mapped[List['Tags']]     = relationship(secondary = ln_users_tags, back_populates = 'users')
  products : Mapped[List['Products']] = relationship(back_populates = 'user')
  orders   : Mapped[List['Orders']]   = relationship(back_populates = 'user')
  posts    : Mapped[List['Posts']]    = relationship(back_populates = 'user')
  docs     : Mapped[List['Docs']]     = relationship(back_populates = 'user')


  # magic
  def __repr__(self):
    return f'Users(id={self.id!r}, email={self.email!r}, password={self.password!r})'
  
  
  # static
  @staticmethod
  def is_default(id):
    try:
      return id == db.session.scalar(
        db.select(Users.id)
          .where(Users.email == USER_EMAIL))
    except:
      pass
    
    return False
  
  
  # public
  def is_company(self):
    return self.includes_tags(POLICY_COMPANY)
  
  # public
  def approved(self):
    return self.includes_tags(POLICY_APPROVED)
  
  # public 
  def disapprove(self):
    error = '@error:disapprove'

    try:
      if self.approved():
        tag_approved = Tags.by_name(POLICY_APPROVED)
        tag_approved.users.remove(self)
        db.session.commit()

    except Exception as e:
      error = e
      raise e
    
    else:
      return str(self.id)
    
    return { 'error': str(error) }
  
  # public
  def approve(self):
    error = '@error:approve'

    try:
      if not self.approved():
        tag_approved = Tags.by_name(POLICY_APPROVED)
        tag_approved.users.append(self)
        db.session.commit()

    except Exception as e:
      error = e
      raise e

    else:
      return str(self.id)
    
    return { 'error': str(error) }, 500
  
  def profile(self):
    p = None
    
    try:

      # get profile tag prefix in .tags
      profile_domain = Docs.docs_profile_domain_from_uid(self.id)
      
      # fetch Tags{}
      t = db.session.scalar(
        db.select(Tags)
          .where(Tags.tag.startswith(profile_domain))
      )
      
      # docid from Tags{}
      docid = int(match_after_last_at(t.tag))

      doc = db.session.get(Docs, docid)
      p   = getattr(doc, 'data')
      
    except:
      pass

    return p if p else {}
  
  def products_sorted_popular(self):
    lsp = []

    sumc = func.sum(ln_orders_products.c.amount)
    ls_p = db.session.scalars(
      db.select(Products, sumc)
        # .join(ln_orders_products)
        # include Products with no orders also
        .join(ln_orders_products, isouter = True)
        .where(Products.user_id == self.id)
        .group_by(Products.id)
        .order_by(desc(sumc))
    )

    lsp = SchemaSerializeProductsTimes(exclude = ('user','user_id',), many = True).dump(ls_p)
    
    return lsp
  
  # public
  def packages_is_premium(self):
    return any([self.packages_is(pkg_type) for pkg_type in PKG.keys()])
  
  # public
  def packages_is(self, pkg_type):
    return self.includes_tags(PKG.get(pkg_type))
  
  # public
  def packages_add(self, pkg_type):
    if not self.packages_is(pkg_type):
      t = Tags.by_name(PKG.get(pkg_type))
      t.users.append(self)
      db.session.commit()  

  # public
  def packages_drop(self, pkg_type):
    if self.packages_is(pkg_type):
      t = Tags.by_name(PKG.get(pkg_type))
      t.users.remove(self)
      db.session.commit()
  
  @staticmethod
  def create_user(*, email, password, company = False):
    u = Users(
      email    = email,
      password = hashPassword(password)
    )
    db.session.add(u)
    db.session.commit()

    if True == company:
      
      # --dev-feature; auto approve companies
      # if `bool:company == true` provided; 
      #   tag user as [company, approved, fs:approved]
      u.tags.append(Tags.by_name(os.getenv('POLICY_COMPANY')))
      u.tags.append(Tags.by_name(os.getenv('POLICY_FILESTORAGE')))

      # @todo; no auto approve
      #  approve users manualy through ui, emails, contacts
      u.tags.append(Tags.by_name(os.getenv('POLICY_APPROVED')))

      db.session.commit()
    
    return u
