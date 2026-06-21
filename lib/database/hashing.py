from argon2 import PasswordHasher

def hash_password(password: str) -> str: return PasswordHasher().hash(password)

def compare_passwords(password: str, stored_hash: str) -> bool:
    r'''
    Compare a password with a hash and return True if the password matches the hash, False otherwise.

    :param password: unencrypted password
    :param stored_hash: hash to compare to
    '''

    try    : return PasswordHasher().verify(stored_hash, password)
    except : return False