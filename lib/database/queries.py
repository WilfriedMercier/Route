import os
import atexit
import dotenv
from   contextlib    import contextmanager
from   psycopg2.pool import ThreadedConnectionPool

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

def execute_query(query: str, values: tuple | None = None):

    try:
        with get_db_connection() as conn:

            cur = conn.cursor()

            if values is None : cur.execute(query)
            else              : cur.execute(query, values)

            results = cur.fetchall()

            return results
        
    except Exception as e: raise e

def insert_hike_into_db(
        user_id   : int,
        hike_name : str,
        hike_dict : dict[str, float | int | list[float]]
    ) -> None:

    lat        = hike_dict['lat']
    lon        = hike_dict['lon']
    zoom       = hike_dict['zoom']
    distances  = hike_dict['distances']
    elevations = hike_dict['elevations']

    query      = '''
        INSERT INTO hikes (name, latitude, longitude, zoom, distances, elevations, user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    '''

    values    = (
        hike_name,
        lat,
        lon,
        zoom,
        distances,  # Array of floats
        elevations,  # Array of floats
        user_id
    )

    execute_query(query, values)

    return