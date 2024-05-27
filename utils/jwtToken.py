import os
import re
from datetime import datetime, timezone

import jwt
from flask import request

# from sqlalchemy import func

from flask_app     import db
from models.tokens import Tokens
from config        import KEY_TOKEN_CREATED_AT


def __with_created_at(payload):
  payload[KEY_TOKEN_CREATED_AT] = str(datetime.now(timezone.utc))
  return payload


def tokenFromRequest():
  return re.match(r'^Bearer (.+)$', request.headers.get('Authorization')).groups()[0]


def decode(sToken):
  return jwt.decode(sToken, os.getenv('JWT_SECRET_ACCESS_TOKEN'), algorithms = ('HS256',))

def decode_secret(sToken, secret):
  return jwt.decode(sToken, secret, algorithms = ('HS256',))

def expired(token):
  jsonTokenPayload = token if isinstance(token, dict) else decode(token)
  ddif = datetime.now(timezone.utc) - datetime.fromisoformat(jsonTokenPayload[KEY_TOKEN_CREATED_AT])
  return int(os.getenv('JWT_EXPIRE_SECONDS')) < ddif.total_seconds()
  

def encode(jsonPayload):
  return jwt.encode(__with_created_at(jsonPayload),
    os.getenv('JWT_SECRET_ACCESS_TOKEN'),
    algorithm = 'HS256'
  )

def encode_secret(jsonPayload, secret):
  return jwt.encode(__with_created_at(jsonPayload),
    secret, algorithm = 'HS256'
  )

def issueToken(jsonPayload):
  # generate/store token @Tokens
  
  token_ = encode(jsonPayload)
  tok    = Tokens(token = token_)
  db.session.add(tok)
  
  db.session.commit()

  return token_
  

def valid(token):
  return Tokens.exists(token)


def setInvalid(token_str):
  tok = None

  try:
    tok = db.session.scalar(
      db.select(Tokens).where(Tokens.token == token_str)
    )
    if None != tok:
      db.session.delete(tok)

  except:
    pass

  else:
    if tok:
      db.session.commit()


def clearExpiredAll():
  i = 0
  tokens = db.session.scalars(db.select(Tokens))
  
  for tok in tokens:
    if expired(tok.token):
      db.session.delete(tok)
      i += 1
  
  if 0 < i:
    db.session.commit()

