import dash
from   flask import session

class HandleShortcut:

    @staticmethod
    def alt_ctrl_l_key_combination(is_hike_panel_open: bool) -> bool:
        r'''
        Handle the Ctrl + Alt + L combination.

        :param is_hike_panel_open: whether the hike panel is open or not

        :returns: True if the hike panel should be opened, False otherwise
        '''

        return not is_hike_panel_open
    
    @staticmethod
    def alt_ctrl_a_key_combination() -> bool:
        r'''
        Handle the Ctrl + Alt + A combination.

        :param is_hike_panel_open: whether the hike panel is open or not

        :returns: True if the user is not connected, False otherwise
        '''

        return 'user_id' not in session

    @staticmethod
    def alt_ctrl_s_key_combination(navbar: dict, burger_opened: bool) -> bool:
        r'''
        Handle the Ctrl + Alt + S combination.

        :param navbar: current state of the navigation bar
        :param burger_opened: whether the burger is opened or closed

        :returns: True if the side panel is closed, False otherwise
        '''

        return not burger_opened