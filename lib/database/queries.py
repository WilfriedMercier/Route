import os
import atexit
import dotenv
from   contextlib    import contextmanager
from   psycopg2.pool import ThreadedConnectionPool
from   psycopg2      import extras

from   ..errors      import NoHikeForMagicLink, NoHikeIDInDB, NoUsernameInDB, NoUserIdInDB
from   ..types       import HikeInfo

# Load environment variables for database
dotenv.load_dotenv()

DB_POOL = ThreadedConnectionPool(
    minconn  = 1,
    maxconn  = 10,
    host     = os.getenv("DB_HOST"),
    dbname   = os.getenv("DB_NAME"),
    user     = os.getenv("DB_USER"),
    password = os.getenv("PGPASSWORD"),
    port     = os.getenv('DB_PORT')
)

@contextmanager
def get_db_connection():
    r"""Context manager for DB connections"""

    conn = DB_POOL.getconn()

    try     : yield conn
    finally : DB_POOL.putconn(conn)

@atexit.register
def close_pool(): DB_POOL.closeall()

def execute_get_query(query: str) -> list[tuple]:
    r'''
    Execute a given fetch query.

    :param query: query to execute

    :raises: any exception if the query execution and fetching fail
    '''

    try:
        with get_db_connection() as conn:

            cur = conn.cursor()
            cur.execute(query)
            results = cur.fetchall()

        return results
        
    except Exception as e: raise e

def execute_query(query: str) -> None:
    r'''
    Execute a given query without fetch.

    :param query: query to execute

    :raises: any exception if the query execution and commit fail
    '''

    try:
        with get_db_connection() as conn:

            cur = conn.cursor()
            cur.execute(query)
            conn.commit()

        return
        
    except Exception as e: raise e

def execute_insert_query(
        query         : str, 
        values        : tuple | list[tuple], 
        multiple_rows : bool = False,
        template      : str | None = None
    ) -> None:
    r'''
    Execute an insert query given some values.

    :param query: query to execute
    :param values: values to pass to the query
    :param multiple_rows: whether multiple rows are passed (True) or just a single row (False) when inserting values
    :param template: template for the values to insert (used when inserting multiple rows)

    :raises: any exception if the query execution and commit fail
    '''

    try:
        with get_db_connection() as conn:

            cur = conn.cursor()

            if multiple_rows : extras.execute_values(cur, query, values, template=template)
            else             : cur.execute(query, values)

            conn.commit()

        return
        
    except Exception as e: raise e

class Users_table:
    r'''A class containing methods that query information in the users table.'''

    @staticmethod
    def get_user_id_from_username(username: str) -> int: 
        r'''
        Return the identifier of the user.

        :param username: name of the user as it appears in the database
        '''

        res = execute_get_query(f"SELECT id FROM users WHERE username = '{username}'")

        if res is None:
            raise NoUsernameInDB(f'The username {username} could not be found in the database.')

        return res[0][0]

    @staticmethod
    def get_username_from_user_id(user_id: int) -> str:
        r'''
        Return the username of the user.

        :param user_id: identifier of the user as it appears in the database
        '''

        res = execute_get_query(f"SELECT username FROM users WHERE id = '{user_id}'")

        if res is None:
            raise NoUserIdInDB(f'User ID {user_id} not found in database.')

        return res[0][0]

class Hikes_table:
    r'''A class containing methods that query information in the hikes table.'''

    @staticmethod
    def get_hike_id_from_user_id_and_hike_name(user_id: int, hike_name: str) -> int:
        '''
        Return the hike id associated to the user if it exists, None otherwise.

        :param user_id: identifier of the user as it appears in the database
        :param hike_name: name of the hike as it appears in the database
        '''
        
        res = execute_get_query(f"SELECT id FROM hikes WHERE user_id = '{user_id}' AND name = '{hike_name}'")

        if res is None or len(res) == 0: 
            raise NoHikeIDInDB(f'Hike with name {hike_name} for user {user_id} not in database.')

        return res[0][0]
    
    @staticmethod
    def is_hike_in_db(user_id: int, hike_name: str) -> bool:
        r'''
        Return True if the hike is in the user's db, False otherwise.

        :param user_id: identifier of the user as it appears in the database
        :param hike_name: name of the hike as it appears in the database
        '''

        try:
            Hikes_table.get_hike_id_from_user_id_and_hike_name(user_id, hike_name)
        except NoHikeIDInDB:
            return False

        return True
    
    @staticmethod
    def insert_hikes_into_db(
        user_id         : int,
        hike_properties : dict[str, HikeInfo],
    ) -> None:
        r'''
        Insert multiple hikes into the database.

        :param user_id: identifier of the user associated to the hikes
        :param hike_properties: dictionary with the hike name as key and a dictionary containing hike properties as values
        '''

        query      = '''
            INSERT INTO hikes (user_id, name, center_lat, center_lon, latitude, longitude, distances, elevations)
            VALUES %s;
        '''

        template = "(%s, %s, %s, %s, %s::double precision[], %s::double precision[], %s::double precision[], %s::double precision[])"

        values = []

        for hike_name, hike_dict in hike_properties.items():

            values.append((
                user_id,
                hike_name,
                hike_dict['center_lat'],
                hike_dict['center_lon'],
                hike_dict['latitudes'],
                hike_dict['longitudes'],
                hike_dict['distances'],
                hike_dict['elevations']
            ))

        execute_insert_query(query, values, multiple_rows=True, template=template)

        return
    
    @staticmethod
    def delete_hike_from_db_given_id(hike_id: str) -> None:
        '''
        Delete a hike with the given ID if it exists in the database.

        :param hike_id: ID of the hike in the hikes table
        '''

        return execute_query(f"DELETE FROM hikes WHERE id = {hike_id}")
    
    @staticmethod
    def delete_hike_from_db_given_name(hike_name: str) -> None:
        '''
        Delete a hike with the given name if it exists in the database.

        :param hike_name: name of the hike in the hikes table
        '''

        return execute_query(f"DELETE FROM hikes WHERE name = '{hike_name}'")

class Magic_links_table:
    r'''A class containing methods that query information in the magic links table.'''

    @staticmethod    
    def get_magic_link_from_hike_id(hike_id: int) -> str | None:
        '''
        Return the magic link id associated to the hike if it exists, None otherwise.

        :param hike_id: identifier of the hike as it appears in the database
        '''

        res = execute_get_query(f"SELECT id FROM magic_links WHERE hike_id = {hike_id}")

        return res[0][0] if len(res) > 0 else None
    
    @staticmethod
    def get_hike_id_from_magic_link(magic_link: str) -> int:
        '''
        Return the hike id the magic link is associated to if the magic link exists, None otherwise.

        :param magic_link: magic link

        :returns: hike ID
        '''

        res = execute_get_query(f"SELECT hike_id FROM magic_links WHERE id = '{magic_link}'")

        if res is None or len(res) != 1: 
            raise NoHikeForMagicLink(f'No hike found for the magic link {magic_link}')
            
        return res[0][0]

    @staticmethod
    def insert_magic_link_into_db(hike_id: int) -> None:
        r'''
        Insert a random UUID as a magic link in the magic_links table in the db.
        
        :param hike_id: identifier of the hike as it appears in the database
        '''

        execute_insert_query(
            f'INSERT INTO magic_links (id, hike_id) VALUES (gen_random_uuid()::text, %s);',
            (hike_id,)
        )

        return