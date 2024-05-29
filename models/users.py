import os
import shutil
from typing import List

from sqlalchemy     import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from . import db
from . import usersTable
from . import ln_users_tags
from . import POLICY_APPROVED
from src.mixins import MixinTimestamps
from src.mixins import MixinIncludesTags

from models.tags     import Tags
from models.docs     import Docs
from models.products import Products

from utils.str import match_after_last_at
from utils.pw  import hash as hashPassword


POLICY_ADMINS         = os.getenv('POLICY_ADMINS')
POLICY_COMPANY        = os.getenv('POLICY_COMPANY')
USER_EMAIL            = os.getenv('USER_EMAIL')
POLICY_PACKAGE_SILVER = os.getenv('POLICY_PACKAGE_SILVER')
POLICY_PACKAGE_GOLD   = os.getenv('POLICY_PACKAGE_GOLD')
TAG_ARCHIVED          = os.getenv('TAG_ARCHIVED')
UPLOAD_PATH           = os.getenv('UPLOAD_PATH')
TAG_EMAIL_VERIFIED    = os.getenv('TAG_EMAIL_VERIFIED')

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
  
  # public
  def accounts_upgrade(self, flag = True):
    isc = self.is_company()
    tt  = Tags.by_name(POLICY_COMPANY)
    
    if flag:
      if not isc:
        tt.users.append(self)
    
    else:
      if isc:
        tt.users.remove(self)
    
    db.session.commit()
    
    return self.is_company()
  
  # public
  def email_verified(self):
    return self.includes_tags(TAG_EMAIL_VERIFIED)
  
  # public
  def set_email_verified(self, flag = True):
    pe  = Tags.by_name(TAG_EMAIL_VERIFIED)
    isv = self.email_verified()
    
    if flag:
      if not isv:
        pe.users.append(self)

    else:
      if isv:
        pe.users.remove(self)
      
    db.session.commit()

    return self.email_verified()
  
  # public
  def is_admin(self):
    return self.includes_tags(POLICY_ADMINS)
  
  # public
  def is_company(self):
    return self.includes_tags(POLICY_COMPANY)
  
  # public
  def approved(self):
    return self.includes_tags(POLICY_APPROVED)
  
  # public
  def set_is_company(self, flag = True):
    pc = Tags.by_name(POLICY_COMPANY)
    iscom = self.is_company()

    if flag:
      if not iscom:
        pc.users.append(self)
    else:
      if iscom:
        pc.users.remove(self)
    
    db.session.commit()

    return self.is_company()
      
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
  
  # public
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
  
  # public
  def is_archived(self):
    return self.includes_tags(TAG_ARCHIVED)
  
  # public
  def set_is_archived(self, flag = True):
    pa   = Tags.by_name(TAG_ARCHIVED)
    isar = self.is_archived()
    
    if flag:
      if not isar:
        pa.users.append(self)
    else:
      if isar:
        pa.users.remove(self)
    
    db.session.commit()

    return self.is_archived()

  # public
  def products_sorted_popular(self):
    return Products.popular_sorted_user(self)
  
  @staticmethod
  def clear_storage(uid):
    directory = os.path.join(UPLOAD_PATH.rstrip("/\\"), 'storage', str(uid))
    if os.path.exists(directory) and os.path.isdir(directory):
      for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
          if os.path.isfile(file_path) or os.path.islink(file_path):
            os.remove(file_path)
            print(f"Removed file: {file_path}")
          elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
            print(f"Removed directory: {file_path}")
        except Exception as e:
          print(f'Failed to delete {file_path}. Reason: {e}')

  @staticmethod
  def create_user(*, email, password, company = False):
    u = Users(
      email    = email,
      password = hashPassword(password)
    )
    db.session.add(u)
    db.session.commit()

    if True == company:
      # company, approved, fs:approved
      u.tags.append(Tags.by_name(os.getenv('POLICY_COMPANY')))
      u.tags.append(Tags.by_name(os.getenv('POLICY_FILESTORAGE')))

    db.session.commit()

    u.approve()
    
    return u

  @staticmethod
  def is_default(id):
    try:
      return id == db.session.scalar(
        db.select(Users.id)
          .where(Users.email == USER_EMAIL))
    except:
      pass
    
    return False
  
  @staticmethod
  def email_exists(email):
    return 0 < db.session.scalar(
      db.select(func.count(Users.id))
        .where(Users.email == email)
    )


  ###########
  ## packages
  
  @staticmethod
  def pasckages_list_is_gold():
    return db.session.scalars(
      db.select(Users)
        .join(Users.tags)
        .where(Tags.tag == POLICY_PACKAGE_GOLD)
    )
    
  @staticmethod
  def pasckages_list_is_silver():
    return db.session.scalars(
      db.select(Users)
        .join(Users.tags)
        .where(Tags.tag == POLICY_PACKAGE_SILVER)
    )
  
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
  
