import dash
from   flask import session

from   ..components.shortcuts import HandleShortcut

def register_keydown_callbacks(app: dash.Dash) -> None:
    r'''
    Register callabacks associated to different key shortcuts being pressed.

    :param app: dash application
    '''
    
    @app.callback(
        dash.Output('hike-panel',       'opened', allow_duplicate=True),
        dash.Output('login-modal',      'opened', allow_duplicate=True),
        dash.Output('burger',           'opened', allow_duplicate=True),
        dash.Output('magic-link-panel', 'opened', allow_duplicate=True),

        dash.Input('keyboard',          'n_keydowns'),
        dash.State('keyboard',          'keydown'),
        dash.State('hike-panel',        'opened'),
        dash.State( "burger",           "opened"),
        dash.State( "magic-link-panel", 'opened'),
        prevent_initial_call=True
    )
    def register_keydown(
            _, 
            keydown                    : dict, 
            is_hike_panel_open         : bool,
            burger_opened              : bool,
            is_magic_link_panel_opened : bool
        ) -> tuple[
            bool | dash.NoUpdate, 
            bool | dash.NoUpdate, 
            bool | dash.NoUpdate,
            bool | dash.NoUpdate
        ]:
        r'''
        Callback called whenever a registered key is pressed. Used to handle shortcuts.

        :param keydown: dictionary with 'key' holding the pressed key and 'altKey' indicating whether alt is pressed as well
        :param is_hike_panel_open: whether the hike panel is open or not

        :returns: 
            - if Ctrl + Alt + L, see :py:`HandleShortcut.alt_ctrl_l_key_combination`
            - if Ctrl + Alt + A, see :py:`HandleShortcut.alt_ctrl_a_key_combination`
            - if Ctrl + Alt + S, see :py:`HandleShortcut.alt_ctrl_s_key_combination`
        '''

        # Shortcut to open/close the hike panel
        if keydown['key'] == 'l' and keydown['altKey'] and keydown['ctrlKey']:
            return (
                HandleShortcut.alt_ctrl_l_key_combination(is_hike_panel_open), 
                dash.no_update,
                dash.no_update,
                dash.no_update
            )
        
        # Shortcut to open the connection modal
        elif (
            not session['magic-link'] and 
            keydown['key'] == 'a' and 
            keydown['altKey'] and
            keydown['ctrlKey']
        ):
            return (
                dash.no_update, 
                HandleShortcut.alt_ctrl_a_key_combination(),
                dash.no_update,
                dash.no_update
            )

        # Shortcut to open the side panel
        elif keydown['key'] == 's' and keydown['altKey'] and keydown['ctrlKey']:

            return (
                dash.no_update,
                dash.no_update,
                HandleShortcut.alt_ctrl_s_key_combination(burger_opened),
                dash.no_update
            )

        # Shortcut to open the magic link panel
        elif (
            not session['magic-link'] and 
            'user_id' in session and
            keydown['key'] == 'm' and 
            keydown['altKey'] and 
            keydown['ctrlKey']
        ):

            return (
                dash.no_update,
                dash.no_update,
                dash.no_update,
                HandleShortcut.alt_ctrl_m_key_combination(is_magic_link_panel_opened)
            )
        
        raise dash.exceptions.PreventUpdate
    
    return