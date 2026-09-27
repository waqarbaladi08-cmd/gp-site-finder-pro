#!/usr/bin/env python3
"""Create an administrator via a private local SQL file, without default credentials.

Password stretching happens in the browser on sign-in to keep the Worker below
the free CPU budget. D1 stores SHA256(hex(PBKDF2(password, random salt, 600000))).
The submitted PBKDF2 value is never stored or logged.
"""
import getpass
import hashlib
import pathlib
import secrets
import sys

def main():
    output=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'private/admin.sql')
    username=input('Administrator username: ').strip()
    if not username or len(username)>100:
        sys.exit('Enter a username between 1 and 100 characters.')
    password=getpass.getpass('New password (at least 12 characters): ')
    if len(password)<12:
        sys.exit('Password must be at least 12 characters.')
    if password!=getpass.getpass('Confirm password: '):
        sys.exit('Passwords do not match.')
    salt=secrets.token_hex(16)
    verifier=hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),600000).hex()
    stored=hashlib.sha256(verifier.encode()).hexdigest()
    quoted=username.replace("'","''")
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(f"INSERT INTO auth_users(username,salt,password_hash,iterations) VALUES('{quoted}','{salt}','{stored}',600000) ON CONFLICT(username) DO UPDATE SET salt=excluded.salt,password_hash=excluded.password_hash,iterations=excluded.iterations;\nDELETE FROM sessions WHERE username='{quoted}';\n")
    output.chmod(0o600)
    print('Private administrator SQL prepared. Password not saved.')

if __name__=='__main__':
    main()
