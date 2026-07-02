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
    '''

    try:
        with get_db_connection() as conn:

            cur = conn.cursor()

            if multiple_rows : extras.execute_values(cur, query, values, template=template)
            else             : cur.execute(query, values, template=template)

            conn.commit()

        return
    
        
    except Exception as e: raise e

def get_user_id(username: str) -> int: 
    r'''
    Return the identifier of the user.

    :param username: name of the user as it appears in the database
    '''

    return execute_get_query(f"SELECT id FROM users WHERE username = '{username}'")[0][0]

def get_username(user_id: int) -> str:
    r'''
    Return the username of the user.

    :param user_id: identifier of the user as it appears in the database
    '''

    return execute_get_query(f"SELECT username FROM users WHERE id = '{user_id}'")[0][0]

def is_hike_in_db(user_id: int, hike_name: str) -> bool:
    r'''
    Check if the hike is in the user's db.

    :param user_id: identifier for the user
    
    :returns: True if in the db, False otherwise
    '''

    res = execute_get_query(f"SELECT name FROM hikes WHERE user_id = '{user_id}' AND name = '{hike_name}'")

    return len(res) > 0

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