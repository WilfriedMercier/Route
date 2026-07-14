from   ..errors   import WrongPassword, WrongUsername
from   .hashing   import compare_passwords
from   .queries   import execute_get_query

def validate_credentials(username: str, password: str) -> bool:
    r'''
    Validate credentials by calling the database.

    :param username: username
    :param password: password

    :returns: True if the combination username, password id correct

    :raises:
        - `WrongUsername` error if the username is wrong whatever the password
        - `WrongPassword` error if the password for the given username
    '''
    
    rows = execute_get_query(f"SELECT password_hash FROM users WHERE username = '{username}'")

    if len(rows) == 0:
        raise WrongUsername(f'Username {username} not found in database.')
    
    if not compare_passwords(password, rows[0][0]):
        raise WrongPassword

    return True