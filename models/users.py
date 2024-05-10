import os
# import json
# import re
from typing import List

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from . import db
from . import usersTable
from . import ln_users_tags
from . import POLICY_APPROVED
from src.mixins import MixinTimestamps
from src.mixins import MixinIncludesTags

from models.tags import Tags
from models.docs import Docs

from utils.str import match_after_last_at

from schemas.serialization import SchemaSerializeDocJsonTimes


POLICY_COMPANY = os.getenv('POLICY_COMPANY')
USER_EMAIL     = os.getenv('USER_EMAIL')

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
  def approve(self):
    error = '@error:internal'

    try:
      if not self.approved():
        tag_approved = Tags.by_name(POLICY_APPROVED)
        tag_approved.users.append(self)
        db.session.commit()

    except Exception as e:
      error = e

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

