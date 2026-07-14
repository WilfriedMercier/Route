import dash
from   flask import session

class HandleShortcut:

    @staticmethod
    def alt_l_key_combination(is_hike_panel_open: bool) -> tuple[bool, dash.NoUpdate]:
        r'''
        Handle the Alt + L combination.

        :param is_hike_panel_open: whether the hike panel is open or not

        :returns: the following tuple
            - True if the hike panel should be opened, False otherwise
            - `dash.no_update`
        '''

        return not is_hike_panel_open, dash.no_update
    
    @staticmethod
    def alt_a_key_combination() -> tuple[dash.NoUpdate, bool]:
        r'''
        Handle the Alt + A combination.

        :param is_hike_panel_open: whether the hike panel is open or not

        :returns: the following tuple
            - `dash.no_update`
            - True if the user is not connected, False otherwise
        '''

        return dash.no_update, 'user_id' not in session