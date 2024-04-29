import os
import json
import re
from typing import List

from sqlalchemy     import JSON
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from . import docsTable
from . import usersTable
from . import postsTable
from . import productsTable
from . import ln_docs_tags
from . import db
from .tags import Tags
from src.mixins import MixinTimestamps
from src.mixins import MixinIncludesTags
from schemas.serialization import SchemaSerializeDocJsonTimes


_prefix_by_doc_id = os.getenv('PREFIX_BY_DOC_ID')

_schemaDocsDump     = SchemaSerializeDocJsonTimes()
_schemaDocsDumpMany = SchemaSerializeDocJsonTimes(many = True)


# https://docs.sqlalchemy.org/en/20/tutorial/metadata.html#declaring-mapped-classes
class Docs(MixinTimestamps, MixinIncludesTags, db.Model):
  __tablename__ = docsTable

  id   : Mapped[int]  = mapped_column(primary_key = True)
  data : Mapped[dict] = mapped_column(JSON)
  user_id    = mapped_column(db.ForeignKey(f'{usersTable}.id'))
  post_id    = mapped_column(db.ForeignKey(f'{postsTable}.id'))
  product_id = mapped_column(db.ForeignKey(f'{productsTable}.id'))

  # virtual
  tags    : Mapped[List['Tags']] = relationship(secondary = ln_docs_tags, back_populates = 'docs')
  user    : Mapped['Users']      = relationship(back_populates = 'docs')
  post    : Mapped['Posts']      = relationship(back_populates = 'docs')
  product : Mapped['Products']   = relationship(back_populates = 'docs')

  
  # magic
  def __repr__(self):
    return f'Docs({json.dumps(self.dump())})'


  @staticmethod
  def tagged(tag_name):
    tag = Tags.by_name(tag_name)
    return tag.docs if tag else []
  
  
  @staticmethod
  def dicts(docs, **kwargs):
    return _schemaDocsDumpMany.dump(docs, **kwargs)
  
  
  @staticmethod
  def by_tag_and_id(tag, id):
    doc = None

    try:
      doc = db.session.scalar(
        db.select(Docs)
          .join(Docs.tags)
          .where(Tags.tag == tag, Docs.id == id))
      
    except:
      pass
    
    return doc


  @staticmethod
  def var_by_name(var_name):
    return db.session.scalar(
      db.select(Docs).join(Docs.tags).where(
        Tags.tag == '@vars', 
        Docs.data.contains(var_name)
      )
    )
  
  
  @staticmethod
  def by_doc_id(doc_id, *, create = False):
    # get single doc by id `doc_id: string` cached in 
    # `@tags.tag` collection, 
    #   ex. `kmPtHAgrysK://foo@56` 
    domain_ = f'{_prefix_by_doc_id}://{doc_id}@'
    tag_    = None
    doc     = None

    try:
      tag_ = db.session.scalar(
        db.select(Tags)
          .where(Tags.tag.like(f'{domain_}%')))
    
    except:
      pass
    
    else:
      if tag_:
        # doc found, resolve
        doc = db.session.get(Docs, re.match(r'.*@(\d+)$', tag_.tag).groups()[0])
      
      else:
        if True == create:
          
          # add default blank doc
          doc = Docs(data = {})          
          db.session.add(doc)
          db.session.commit()
          
          # add related tag
          tag_ = Tags(tag = f'{domain_}{doc.id}')
          db.session.add(tag_)
          db.session.commit()

    return doc
    
    
  def dump(self, **kwargs):
    return _schemaDocsDump.dump(self, **kwargs)
