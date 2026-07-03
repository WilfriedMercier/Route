import os
import atexit
import dotenv
from   contextlib    import contextmanager
from   psycopg2.pool import ThreadedConnectionPool
from   psycopg2      import extras

# Load environment variables for database
dotenv.load_dotenv()

DB_POOL = ThreadedConnectionPool(
    minconn  = 1,
    maxconn  = 10,
    host     = os.getenv("DB_HOST"),
    dbname   = os.getenv("DB_NAME"),
    user     = os.getenv("DB_USER"),
    password = os.getenv("DB_PASSWORD"),
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
    Execute a fetch query given some values.

    :param query: query to execute
    '''

    try:
        with get_db_connection() as conn:

            cur = conn.cursor()
            cur.execute(query)
            results = cur.fetchall()

        return results
        
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

        return execute_get_query(f"SELECT id FROM users WHERE username = '{username}'")[0][0]

    @staticmethod
    def get_username_from_user_id(user_id: int) -> str:
        r'''
        Return the username of the user.

        :param user_id: identifier of the user as it appears in the database
        '''

        return execute_get_query(f"SELECT username FROM users WHERE id = '{user_id}'")[0][0]

class Hikes_table:
    r'''A class containing methods that query information in the hikes table.'''

    @staticmethod
    def get_hike_id_from_user_id_and_hike_name(user_id: int, hike_name: str) -> int | None:
        '''
        Return the hike id associated to the user if it exists, None otherwise.

        :param user_id: identifier of the user as it appears in the database
        :param hike_name: name of the hike as it appears in the database
        '''

        res = execute_get_query(f"SELECT id FROM hikes WHERE user_id = '{user_id}' AND name = '{hike_name}'")

        return res[0][0] if len(res) > 0 else None
    
    @staticmethod
    def is_hike_in_db(user_id: int, hike_name: str) -> bool:
        r'''
        Return True if the hike is in the user's db, False otherwise.

        :param user_id: identifier of the user as it appears in the database
        :param hike_name: name of the hike as it appears in the database
        '''

        return Hikes_table.get_hike_id_from_user_id_and_hike_name(user_id, hike_name) is not None
    
    @staticmethod
    def insert_hikes_into_db(
        user_id         : int,
        hike_properties : dict[str, dict[str, float | int | list[float]]],
    ) -> None:
        r'''
        Insert multiple hikes into the database.

        :param user_id: identifier of the user associated to the hikes
        :param hike_properties: dictionary with the hike name as key and a dictionary containing hike properties as values
        '''

        query      = '''
            INSERT INTO hikes (user_id, name, center_lat, center_lon, zoom, latitude, longitude, distances, elevations)
            VALUES %s;
        '''

        template = "(%s, %s, %s, %s, %s, %s::double precision[], %s::double precision[], %s::double precision[], %s::double precision[])"

        values = []

        for hike_name, hike_dict in hike_properties.items():

            center: list[float] = hike_dict['center'] # type: ignore

            values.append((
                user_id,
                hike_name,
                center[0],
                center[1],
                hike_dict['zoom'],
                hike_dict['lat'],
                hike_dict['lon'],
                hike_dict['distances'],
                hike_dict['elevations'],
            ))

        execute_insert_query(query, values, multiple_rows=True, template=template)

        print('Here is the db')
        print(execute_get_query('SELECT * FROM hikes;'))

        return

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
    def get_hike_id_from_magic_link(magic_link: str) -> int | None:
        '''
        Return the hike id the magic link is associated to if the magic link exists, None otherwise.

        :param magic_link: magic link
        '''

        res = execute_get_query(f"SELECT hike_id FROM magic_links WHERE id = '{magic_link}'")

        return res[0][0] if len(res) > 0 else None


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