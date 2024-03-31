import os

# from sqlalchemy import func

from flask_app    import db
from flask_app    import APP_NAME
from models.users import Users
from models.tags  import Tags
from models.docs  import Docs
from .            import init_docs_tags
from config       import TAG_VARS
from utils.pw     import hash as hashPassword


for t in init_docs_tags:
  Tags.by_name(t, create = True)

tag_vars = Tags.by_name(TAG_VARS)

vars_data = [doc.data for doc in tag_vars.docs]

if all(not 'app:name' in node for node in vars_data):
  tag_vars.docs.append(Docs(data = { 'app:name': APP_NAME }))

if all(not 'admin:email' in node for node in vars_data):
  tag_vars.docs.append(Docs(data = { 'admin:email': os.getenv('ADMIN_EMAIL') }))
  
db.session.commit()


# add default users --admin --user
email_    = os.getenv('ADMIN_EMAIL')
password_ = os.getenv('ADMIN_PASSWORD')

emailUser_    = os.getenv('USER_EMAIL')
passwordUser_ = os.getenv('USER_PASSWORD')

user_admin   = db.session.scalar(db.select(Users).where(Users.email == email_))
user_default = db.session.scalar(db.select(Users).where(Users.email == emailUser_))

if not user_admin:
  user_admin = Users(email = email_, password = hashPassword(password_))
  db.session.add(user_admin)

if not user_default:
  user_default = Users(email = emailUser_, password = hashPassword(passwordUser_))
  db.session.add(user_default)

db.session.commit()


# store default tags
policy_admins_           = os.getenv('POLICY_ADMINS')
policy_email_            = os.getenv('POLICY_EMAIL')
policy_fs_               = os.getenv('POLICY_FILESTORAGE')
policy_all_              = os.getenv('POLICY_ALL')
policy_company_          = os.getenv('POLICY_COMPANY')
# policy_company_approved_ = os.getenv('POLICY_COMPANY_APPROVED')
policy_approved_         = os.getenv('POLICY_APPROVED')

tagPolicyADMINS           = Tags.by_name(policy_admins_,  create = True)
tagPolicyEMAIL            = Tags.by_name(policy_email_,   create = True)
tagPolicyFS               = Tags.by_name(policy_fs_,      create = True)
tagPolicyALL              = Tags.by_name(policy_all_,     create = True)
tagPolicyCOMPANY          = Tags.by_name(policy_company_, create = True)
# tagPolicyCOMPANY_approved = Tags.by_name(policy_company_approved_, create = True)
tagPolicy_approved        = Tags.by_name(policy_approved_, create = True)


# tag default users
if not user_admin.includes_tags(policy_admins_):
  tagPolicyADMINS.users.append(user_admin)
if not user_admin.includes_tags(policy_email_):
  tagPolicyEMAIL.users.append(user_admin)
if not user_admin.includes_tags(policy_fs_):
  tagPolicyFS.users.append(user_admin)
if not user_admin.includes_tags(policy_company_):
  tagPolicyCOMPANY.users.append(user_admin)
if not user_admin.includes_tags(policy_approved_):
  tagPolicy_approved.users.append(user_admin)
# if not user_admin.includes_tags(policy_all_):
#   tagPolicyALL.users.append(user_admin)

if not user_default.includes_tags(policy_email_):
  tagPolicyEMAIL.users.append(user_default)
if not user_default.includes_tags(policy_fs_):
  tagPolicyFS.users.append(user_default)

db.session.commit()

