import os
import dotenv
import logging
import getpass
import argparse
import psycopg2
from   argon2   import PasswordHasher

dotenv.load_dotenv()

def main(username: str, hash: str) -> None:

    # Connect to database
    try:
        with psycopg2.connect(
                database = os.getenv('DB_NAME'),
                user     = os.getenv('DB_USER'),
                host     = os.getenv('DB_HOST'),
                port     = os.getenv('DB_PORT'),
                password = os.getenv('PGPASSWORD')
            ) as conn:

            cur = conn.cursor()

            # Execute insert query
            cur.execute(f"INSERT INTO users (username, password_hash) VALUES ('{username}', '{hash}');")
    except psycopg2.OperationalError as e:
        logging.error(f'Database connection failed with error message {e}')

    return

if __name__ == '__main__': 
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        prog        = 'Insert user into db',
        description = 'Script that insert a user into the Route db.',
        add_help    = True
    )

    parser.add_argument('-u', '--user',     dest='username', help='Username to add to the database.')
    args = parser.parse_args()

    if args.username is None: raise IOError('Missing username.')

    # Hash password with argon2
    hash = PasswordHasher().hash(
        getpass.getpass('Enter password:')
    )
    
    main(args.username, hash)