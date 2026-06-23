import os
import psycopg2
from .hashing   import hash_password, compare_passwords

def validate_credentials(username: str, password: str) -> bool | None:
    r'''
    Validate credentials by calling the database.

    :param username: username
    :param password: password

    :returns: 
        - None if the user does not exist
        - True if credentials are valid, False otherwise.
    '''

    conn = psycopg2.connect(
        dbname   = os.getenv('DB_NAME'),
        host     = os.getenv('DB_HOST'),
        port     = os.getenv('DB_PORT'),
        user     = os.getenv('DB_USER'),
        password = os.getenv('DB_PASSWORD')
    )

    cursor = conn.cursor()
    
    cursor.execute(f"SELECT password_hash FROM users WHERE username = '{username}'")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    if len(rows) == 0: return None
    else: 
        
        hash = rows[0][0]
        
        return compare_passwords(password, hash)