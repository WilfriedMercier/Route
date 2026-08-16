import os
import atexit
import dotenv
from   contextlib    import contextmanager
from   psycopg2.pool import ThreadedConnectionPool
from   psycopg2      import extras
from   psycopg2.sql  import Identifier, SQL, Composable

from   ..types       import HikeInfo
from   ..errors      import (
    NoHikeForMagicLink, 
    NoHikeIDInDB, 
    NoUsernameInDB, 
    NoUserIdInDB, 
    NoMagicLinkForHikeID,
    NoHikeForUser,
    NoMagicLinkIDInDB
)


# Load environment variables for database
dotenv.load_dotenv()

DB_POOL = ThreadedConnectionPool(
    minconn     = 1,
    maxconn     = 10,
    host        = os.getenv("DB_HOST"),
    dbname      = os.getenv("DB_NAME"),
    user        = os.getenv("DB_USER"),
    password    = os.getenv("PGPASSWORD"),
    port        = os.getenv('DB_PORT'),
    sslmode     = os.getenv('SSLMODE'),
    sslrootcert = os.getenv('SSLCERTIFICATE')
)

@contextmanager
def get_db_connection():
    r"""Context manager for DB connections"""

    conn = DB_POOL.getconn()

    try     : yield conn
    finally : DB_POOL.putconn(conn)

@atexit.register
def close_pool(): DB_POOL.closeall()

def execute_query(query: str | Composable) -> None:
    r'''
    Execute a given query without parameters and without returning its output.

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

def execute_query_with_params(
        query         : str | Composable, 
        values        : tuple | list[tuple] | None = None,
        multiple_rows : bool = False,
        template      : str | None = None
    ) -> None:
    r'''
    Execute a query with parameters.

    :param query: query to execute
    :param values: values to pass to the query. If None, no values are passed.
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

def execute_get_query(query: str | Composable) -> list[tuple]:
    r'''
    Execute a query without parameters that returns its output.

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

def execute_get_query_with_params(
        query         : str | Composable, 
        values        : tuple | list[tuple] | None = None,
        multiple_rows : bool = False,
        template      : str | None = None,
        commit        : bool = False
    ) -> list[tuple]:
    r'''
    Execute a query with parameters that returns its outputs.

    :param query: query to execute
    :param values: values to pass to the query. If None, no values are passed.
    :param commit: whether to commit the transaction or not
    :param values: values to pass to the query. If None, no values are passed.
    :param multiple_rows: whether multiple rows are passed (True) or just a single row (False) when inserting values

    :raises: any exception if the query execution and commit fail
    '''

    try:
        with get_db_connection() as conn:

            cur = conn.cursor()

            if multiple_rows : extras.execute_values(cur, query, values, template=template)
            else             : cur.execute(query, values)

            if commit: conn.commit()

            results = cur.fetchall()

        return results
        
    except Exception as e: raise e

class Users_table:
    r'''A class containing methods that query information in the users table.'''

    _table = 'users'

    @classmethod
    def get_user_id_from_username(cls, username: str) -> int: 
        r'''
        Return the identifier of the user.

        :param username: name of the user as it appears in the database
        '''

        res = execute_get_query_with_params(
            SQL("SELECT id FROM {} WHERE username = %s").format(Identifier(cls._table)),
            values = (username,)
        )

        if res is None:
            raise NoUsernameInDB(f'The username {username} could not be found in the database.')

        return res[0][0]

    @classmethod
    def get_username_from_user_id(cls, user_id: int) -> str:
        r'''
        Return the username of the user.

        :param user_id: identifier of the user as it appears in the database
        '''

        res = execute_get_query_with_params(
            SQL("SELECT username FROM {} WHERE id = %s").format(Identifier(cls._table)),
            values = (user_id,)
        )

        if res is None:
            raise NoUserIdInDB(f'User ID {user_id} not found in database.')

        return res[0][0]

class Hikes_table:
    r'''A class containing methods that query information in the hikes table.'''

    _table = 'hikes'

    @classmethod
    def get_rows_from_user_id(
            cls, 
            user_id : int,
            columns : list[str] | None = None
        ) -> list[tuple]:
        '''
        Return all the rows associated to the user ID.

        :param user_id: identifier of the user as it appears in the database
        :param columns: column names to retrieve. If None, all columns are returned as shown below.
        
        :returns: all the rows with the provided column names. If columns is None, all columns are returned in the following order:
            - hike's id
            - hike's name
            - hike's latitude array
            - hike's longitude array
            - hike's center latitude
            - hike's center longitude
            - hike's distance array
            - hike's elevation array
            - hike's color
        '''

        if columns is None:
            columns = ["id", "name", "latitude", "longitude", "center_lat", "center_lon", "distances", "elevations", "color"]
        
        res = execute_get_query_with_params(
            SQL("""
                SELECT {columns}
                FROM {table}
                WHERE user_id = %s
            """).format(
                columns = SQL(', ').join(map(Identifier, columns)),
                table   = Identifier(cls._table)
            ),
            values = (user_id,)
        )

        if res is None or len(res) == 0: 
            raise NoHikeForUser(f'No hikes with for user {user_id} in database.')

        return res

    @classmethod
    def get_row_from_hike_id(
            cls, 
            hike_id: int, 
            columns : list[str] | None = None
        ) -> tuple:
        '''
        Return the row associated to the hike ID.

        :param hike_id: id of the hike
        :param columns: column names to retrieve. If None, all columns are returned as shown below.
        
        :returns: all the rows with the provided column names. If columns is None, all columns are returned in the following order:
            - user's id associated to the hike
            - hike's name
            - hike's latitude array
            - hike's longitude array
            - hike's center latitude
            - hike's center longitude
            - hike's distance array
            - hike's elevation array
        '''

        if columns is None:
            columns = ["user_id", "name", "latitude", "longitude", "center_lat", "center_lon", "distances", "elevations"]   
        
        res = execute_get_query_with_params(
            SQL("""
                SELECT {columns}
                FROM {table}
                WHERE id = %s
            """).format(
                columns = SQL(', ').join(map(Identifier, columns)),
                table   = Identifier(cls._table)
            ),
            (hike_id,)
        )

        if res is None or len(res) != 1: 
            raise NoHikeIDInDB(f'No hike with id {hike_id} in database.')

        return res[0]

    @classmethod
    def get_rows_from_hike_ids(
        cls,
        hike_ids : list[int],
        columns  : list[str] | None
    ) -> list[tuple]:
        r'''
        Return the rows associated to the hike IDs in the same order as they appear in hike_ids.

        .. note::

            Whether you provide 'id' as a column or not and in whatever position, 'id' will always ne returned as the first element of the output tuples
        
        :param user_id: ids of the hikes to select
        :param columns: column names to retrieve. If None, all columns are returned as shown below.
        
        :returns: all the rows with the provided column names. If columns is None, all columns are returned in the following order:
            - hike id
            - user's id associated to the hike
            - hike's name
            - hike's latitude array
            - hike's longitude array
            - hike's center latitude
            - hike's center longitude
            - hike's distance array
            - hike's elevation array
        '''

        if columns is None:
            columns = ["id", "user_id", "name", "latitude", "longitude", "center_lat", "center_lon", "distances", "elevations"]
        else:

            # Make sure that id is always the first columns
            if columns[0] != 'id' and 'id' in columns:
                columns.remove('id')
            if 'id' not in columns:
                columns = ['id'] + columns
        
        res = execute_get_query_with_params(
            SQL("""
                SELECT {columns}
                FROM {table}
                WHERE id = ANY(%s)
            """).format(
                columns = SQL(', ').join(map(Identifier, columns)),
                table   = Identifier(cls._table)
            ),
            (hike_ids,)
        )

        if res is None: 
            raise NoHikeIDInDB(f'No hike with id in {hike_ids} in database.')
        elif len(res) == 0:
            return res

        # We reorder the outputs so that it matches the input order
        res_ids = [i[0] for i in res]
        out     = []

        for hike_id in hike_ids:

            pos = res_ids.index(hike_id)
            out.append(res[pos])

        return out

    @classmethod
    def get_hike_name_from_hike_id(cls, hike_id: int) -> str:
        '''
        Return the name of the hike associated to the given hike ID.

        :param hike_id: ID of the hike
        '''

        res = cls.get_row_from_hike_id(hike_id, columns = ['name'])

        return res[0]

    @classmethod
    def get_hike_id_from_user_id_and_hike_name(cls, user_id: int, hike_name: str) -> int:
        '''
        Return the hike id associated to the user if it exists, None otherwise.

        :param user_id: identifier of the user as it appears in the database
        :param hike_name: name of the hike as it appears in the database
        '''
        
        res = execute_get_query_with_params(
            SQL("""
                SELECT id FROM {} 
                WHERE user_id = %s AND name = %s
            """).format(Identifier(cls._table)),
            values = (user_id, hike_name)
        )

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
    
    @classmethod
    def insert_hikes_into_db(
        cls,
        user_id         : int,
        hike_properties : dict[str, HikeInfo],
    ) -> None:
        r'''
        Insert multiple hikes into the database.

        :param user_id: identifier of the user associated to the hikes
        :param hike_properties: dictionary with the hike name as key and a dictionary containing hike properties as values
        '''

        query      = f'''
            INSERT INTO {cls._table} (user_id, name, center_lat, center_lon, latitude, longitude, distances, elevations)
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

        execute_query_with_params(query, values, multiple_rows=True, template=template)

        return
    
    @classmethod
    def delete_hike_from_db_given_id(cls, hike_id: str) -> None:
        '''
        Delete a hike with the given ID if it exists in the database.

        :param hike_id: ID of the hike in the hikes table
        '''

        return execute_query_with_params(
            SQL("DELETE FROM {} WHERE id = %s").format(Identifier(cls._table)),
            values = (hike_id,)
        )
    
    @classmethod
    def delete_hike_from_db_given_name(cls, hike_name: str) -> None:
        '''
        Delete a hike with the given name if it exists in the database.

        :param hike_name: name of the hike in the hikes table
        '''

        execute_query_with_params(
            SQL("DELETE FROM {} WHERE name = %s").format(Identifier(cls._table)),
            values = (hike_name,)
        )

        return

class Magic_links_table:
    r'''A class containing methods that query information in the magic links table.'''

    _table = 'magic_links'

    @classmethod
    def get_magic_link_name(cls, magic_link: str) -> str:
        '''
        Returns the name of the given magic link
        
        :param magic_link: magic link
        '''

        res = execute_get_query_with_params(
            SQL("""
                SELECT name FROM {}
                WHERE id = %s
            """).format(Identifier(cls._table)),
            values = (magic_link,)
        )

        if res is None or len(res) != 1: 
            raise NoMagicLinkIDInDB(f'No magic link {magic_link} found in database.')

        return res[0][0]

    @classmethod
    def update_magic_link_name(cls, magic_link: str, name: str) -> None:
        '''
        Update the name field in the magic links table for a given magic link.

        :param magic_link: magic link
        :param name: name value to be updated in the corresponding row
        '''

        execute_query_with_params(
            SQL('''
                UPDATE {}
                SET name = %s
                WHERE id = %s
            ''').format(Identifier(cls._table)),
            values = (name, magic_link)
        )

        return

    @classmethod
    def get_rows(cls) -> list[tuple[str, str, int]]:
        r'''
        Return all the rows from the table.
        
        :returns: rows with columns in that order
            - magic link
            - magic link name
            - associated user id
        '''

        res = execute_get_query(
            SQL("SELECT id, name, user_id FROM {}").format(Identifier(cls._table))
        )

        if res is None or len(res) == 0: return []

        return [i[0] for i in res]

    @classmethod
    def get_rows_from_user_id(cls, user_id: int) -> list[tuple[str, str]]:
        r'''
        Return all the rows from the table associated to the given user.

        :returns: all rows with columns as follows
            - magic link
            - magic link name
        '''

        res = execute_get_query_with_params(
            SQL("""
                SELECT id, name 
                FROM {}
                WHERE user_id = %s
            """).format(Identifier(cls._table)),
            (user_id,)
        )

        return res

    @classmethod
    def insert_row(cls, name: str, user_id: int) -> str:
        r'''
        Generate and insert a random UUID as a magic link in the table.
        
        :param name: name of the magic link shown in the UI
        :param user_id: id of the user

        :returns: the newly created magic link
        '''

        res = execute_get_query_with_params(
            SQL('''
                INSERT INTO {} (id, name, user_id) 
                VALUES (gen_random_uuid()::text, %s, %s)
                RETURNING id;
            ''').format(Identifier(cls._table)),
            (name, user_id),
            commit = True
        )[0][0]

        return res

    @classmethod
    def delete_row(cls, magic_link: str) -> None:
        r'''
        Delete the row in the magic links table (and other tables via cascade) with the given magic link.

        :param magic_link: magic link
        '''

        execute_query_with_params(
            SQL('''
                DELETE FROM {}
                WHERE id = %s
            ''').format(Identifier(cls._table)),
            values = (magic_link,)
        )

        return

class Magic_links_props_table:
    r'''A class containing methods that query information in the magic links props table.'''

    _table = 'magic_links_props'

    @classmethod    
    def get_magic_links_from_hike_id(cls, hike_id: int) -> list[str]:
        r'''
        Return all the magic links associated to the hike if it exists.

        :param hike_id: identifier of the hike as it appears in the database
        '''

        res = execute_get_query_with_params(
            SQL("SELECT id FROM {} WHERE hike_id = %s").format(Identifier(cls._table)),
            values = (hike_id,)
        )

        if res is None or len(res) == 0: 
            raise NoMagicLinkForHikeID(f'No magic link found for hike {hike_id}.')

        return [i[0] for i in res]
    
    @classmethod
    def get_hike_ids_from_magic_link(cls, magic_link: str) -> list[int]:
        r'''
        Return all the hike ids the magic link is associated to if the magic link exists.

        :param magic_link: magic link

        :returns: hike ID
        '''

        res = execute_get_query_with_params(
            SQL("SELECT hike_id FROM {} WHERE id = %s").format(Identifier(cls._table)),
            values = (magic_link,)
        )

        if res is None: raise NoHikeForMagicLink(f'No hike found for the magic link {magic_link}.')

        return [i[0] for i in res]

    @classmethod
    def get_rows_from_magic_link(cls, magic_link: str) -> list[tuple[int, str, int]]:
        r'''
        Return all the properties associated to the magic link.

        :param hike_ids: tuple containing all the hike ids one wants to get the rows from

        :returns: all the rows for the given magic link with columns as follows
            - hike id
            - color
        '''

        res = execute_get_query_with_params(
            SQL('''
                SELECT hike_id, color
                FROM {}
                WHERE id = %s
            ''').format(Identifier(cls._table)),
            (magic_link,)
        )

        return res

    @classmethod
    def get_rows_from_hike_ids(cls, hike_ids: tuple[int]) -> list[tuple]:
        r'''
        Return all the rows associated to the hike id.

        :param hike_ids: tuple containing all the hike ids one wants to get the rows from

        :returns: all the rows where hike_id is in hike_ids in the following order
            - id (magic link)
            - hike_id
            - color
        '''

        res = execute_get_query_with_params(
            SQL('''
                SELECT id, hike_id, color
                FROM {}
                WHERE hike_id IN %s
            ''').format(Identifier(cls._table)),
            values = (hike_ids,)
        )

        if res is None or len(res) == 0: 
            raise NoMagicLinkForHikeID(f'No rows found for hikes {hike_ids}.')

        return res

    @classmethod
    def insert_row(cls, magic_link: str, hike_id: int, color: str) -> None:
        r'''
        Insert a new row in the table.
        
        :param magic_link: magic link associated to the hike
        :param hike_id: identifier of the hike as it appears in the database
        :param color: color associated to the hike
        '''

        execute_query_with_params(
            SQL('''
                INSERT INTO {} (id, hike_id, color) 
                VALUES (%s, %s, %s);
            ''').format(Identifier(cls._table)),
            (magic_link, hike_id, color)
        )

        return 