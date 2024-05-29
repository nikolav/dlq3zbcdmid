import os
from flask import g
from flask import render_template

from flask_mail import Message

from flask_app import db
from flask_app import mail

from models.users import Users

from utils.jwtToken      import encode_secret
from config.graphql.init import mutation


JWT_SECRET_VERIFY_EMAIL = os.getenv('JWT_SECRET_VERIFY_EMAIL')

@mutation.field('accountsSendVerifyEmailLink')
def resolve_accountsSendVerifyEmailLink(_o, _i, uid, url):
  res = None
  try:
    u = db.session.get(Users, uid)

    if u.email_verified():
      raise Exception('access denied')
      
    if not u.id == g.user.id:
      raise Exception('access denied')
        
    key = encode_secret({ 'uid': u.id, 'email': u.email }, 
                        JWT_SECRET_VERIFY_EMAIL)
    
    res = mail.send(
      Message(
        
        # subject
        'potvrda-email-adrese@kantar.rs',

        # from
        sender = ('KANTAR.RS', 'app@kantar.rs'),
        
        # default recepiens ls
        recipients = [u.email],
        
        # pass all data to mail template
        html = render_template(
          'mail/auth-verify-email.html', 
          url = f'{str(url).rstrip("/")}/?key={key}')
      )
    )
    
  except Exception as err:
    raise err

  else:
    return u.id if not res else None
  
  return None

