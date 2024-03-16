# import os
# import json
# import re
# from typing import List

from sqlalchemy import func

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
# from sqlalchemy.orm import relationship

from . import db
from . import tblSuffix
from src.mixins import MixinTimestamps


tablename_tokens  = 'tokens'
tablename_tokens_ = f'{tablename_tokens}{tblSuffix}'

class Tokens(MixinTimestamps, db.Model):
  __tablename__ = tablename_tokens_
  
  id: Mapped[int] = mapped_column(primary_key = True)
  
  token: Mapped[str] = mapped_column(unique = True)


  # magic
  def __repr__(self):
    return f'Tokens(id={self.id!r}, token={self.token!r})'

  @staticmethod
  def exists(str_token):
    try:
      return 0 < db.session.scalar(
        db.select(func.count(Tokens.id)).where(Tokens.token == str_token)
      )
    except:
      pass
    
    return False

  