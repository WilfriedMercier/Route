from   flask   import session

from .database import Hikes_table

def check_if_hike_is_loaded(hike_name: str, hike_list: list[str]):
    r'''
    Check if the given hike is in either the database if the user is logged in or in the hikes already loaded if not logged in.

    :param hike_name: name of the hike
    :param hike_list: list of hikes already loaded

    :returns: True if the hike is already loaded, False otherwise
    '''

    # Case when the user is logged in
    if 'user_id' in session: is_in_db = Hikes_table.is_hike_in_db(session['user_id'], hike_name)

    # Case when the user is not logged in
    else: is_in_db = hike_name in hike_list

    return is_in_db