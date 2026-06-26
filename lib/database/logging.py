import os
import psycopg2

from   .hashing   import compare_passwords
from   .queries   import execute_query

def validate_credentials(username: str, password: str) -> bool | None:
    r'''
    Validate credentials by calling the database.

    :param username: username
    :param password: password

    :returns: 
        - None if the user does not exist
        - True if credentials are valid, False otherwise.
    '''
    
    rows = execute_query(f"SELECT password_hash FROM users WHERE username = '{username}'")
    
    if len(rows) == 0: return None
    else: return compare_passwords(password, rows[0][0])