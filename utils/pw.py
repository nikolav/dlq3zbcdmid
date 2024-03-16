
import bcrypt

def hash(sPassword):
  bPassword       = sPassword.encode()
  bPasswordHashed = bcrypt.hashpw(bPassword, bcrypt.gensalt())
  return bPasswordHashed.hex()

def check(sPassword, hexPasswordHashed):
  bPassword       = sPassword.encode()
  bPasswordHashed = bytes.fromhex(hexPasswordHashed)
  return bcrypt.checkpw(bPassword, bPasswordHashed)
