import dash
import typing
import dash_leaflet            as     dl
import dash_mantine_components as     dmc
from   flask                   import session

from ..lang                     import LANGUAGE
from ..database                 import validate_credentials, Users_table
from ..components.map           import generate_leaflet_map_figure
from ..components.notifications import login_success_notification, logout_success_notification

from .misc                      import (
    generate_hike_ui_elements_with_login,
    generate_magic_link_container_rows_from_db
)

from ..errors   import (
    WrongPassword, 
    WrongUsername, 
    NoUsernameInDB, 
    NoUserIdInDB
)

from ..types import (
    Dummy,
    HikeInfo, 
    HikeProps, 
    HikeDataForMarker, 
    HikeDataForElevationPlot, 
    Notification
)

def register_login_callbacks(app: dash.Dash) -> None:
    r'''
    Register all callbacks associated to logging in.

    :param app: dash application
    '''

    # Focus to username field when modal opens
    app.clientside_callback(
        """
        function(is_open) {
            if (is_open) {
                setTimeout(function() {
                    var el = document.getElementById('login-modal-id-input');
                    if (el) { el.focus(); }
                }, 100);
            }
            return window.dash_clientside.no_update;
        }
        """,
        dash.Output("login-modal-id-input", "key"),  # dummy output
        dash.Input({'type' : "login-button", 'index' : dash.ALL}, "n_clicks"),
    )

    @app.callback(
        dash.Output('login-modal', 'opened', allow_duplicate=True),

        dash.Output('map-div', 'style', allow_duplicate=True),
        dash.Output('elevation-plot-stack', 'style', allow_duplicate=True),
        dash.Output('dummy',   'data', allow_duplicate=True),

        dash.Output('login-modal-id-input', 'error'),
        dash.Output('login-modal-password-input', 'error'),

        dash.Input('send-login-button', 'n_clicks'),
        dash.Input('login-modal-id-input', 'n_submit'),
        dash.Input('login-modal-password-input', 'n_submit'),
        dash.State('login-modal-id-input', 'value'),
        dash.State('login-modal-password-input', 'value'),
        dash.State('language', 'data'),
        dash.State('dummy', 'data'),
        prevent_initial_call=True
    )
    def secure_login_first_pass(
            _1, _2, _3,
            username : str, 
            password : str,
            language : LANGUAGE,
            dummy    : Dummy
        ) -> tuple[
            bool,
            dict[str, str] | dash.NoUpdate, dict[str, str] | dash.NoUpdate,
            Dummy | dash.NoUpdate,
            str   | dash.NoUpdate, str | dash.NoUpdate
        ]:
        r'''
        Callback used when the user is trying to login.

        .. note:
            This is the first pass that handles login and resizes the map. The second pass is called when

        :param username: username provided in the relevant field
        :param password: password provided in the relevant field
        :param language: current language of the application
        :param dummy: a dummy object used to trigger the secondary callback if the username and password are correct
        '''

        translation = app.language_handler[language]

        # If one of the fields is empty, we let the page as is
        if password is None or username is None or password == '' or username == '':
            raise dash.exceptions.PreventUpdate

        try:
            validate_credentials(username, password)

        # Handle cases where the username or password are wrong
        except WrongUsername: return (
                True, 
                dash.no_update, dash.no_update, 
                dash.no_update, 
                translation['login_modal']['user_id_input']['error'], ''
            )
        
        except WrongPassword: return (
                True, 
                dash.no_update, dash.no_update, 
                dash.no_update, 
                '', translation['login_modal']['user_password_input']['error']
            )
        
        # Password and username are both correct, we store the user ID for later queries into the database
        try:
            session['user_id'] = Users_table.get_user_id_from_username(username)
        except NoUsernameInDB: raise dash.exceptions.PreventUpdate
        
        return (
            False,
            {'height' : '70%'}, {'display' : 'flex'},
            Dummy(n_clicks = dummy['n_clicks'] + 1, type = 'login'),
            dash.no_update, dash.no_update
        )
        
    @app.callback(
        dash.Output('map-div', 'children', allow_duplicate=True),
        dash.Output('notification-container', 'sendNotifications'),

        dash.Output({'type' : 'login-button', 'index' : dash.ALL}, 'children', allow_duplicate=True),
        dash.Output({'type' : 'login-button-tooltip', 'index' : dash.ALL}, 'label', allow_duplicate=True),

        dash.Output('hikelist-div', 'children', allow_duplicate=True),
        dash.Output('number-hikes', 'data', allow_duplicate=True),
        dash.Output('hikes-info',   'data', allow_duplicate=True),

        dash.Output('map-polylines', 'children', allow_duplicate=True),

        dash.Output('magic-link-button', 'disabled'),
        dash.Output('magic-link-button-tooltip', 'disabled'),

        dash.Output('magic-link-container', 'children', allow_duplicate=True),
        
        dash.Input('dummy', 'data'),
        dash.State('language', 'data'),

        prevent_initial_call=True
    )
    def secure_login_second_pass(
        dummy    : Dummy,
        language : LANGUAGE
        ) -> tuple[
            dl.Map, # map -> children
            list[Notification],

            tuple[str, str],
            tuple[str, str],
            
            list[dmc.Space],
            int,
            dict[str, HikeInfo],

            list[dl.Polyline],

            typing.Literal[False],
            typing.Literal[False],

            list[dmc.Stack]
        ]:
        r'''
        Callback used when the user is trying to login.

        :param dummy: dummy object used to trigger this callback
        :param language: current language of the application
        '''

        # No action taken if the dummy is not triggered by the first pass of the UI update
        if dummy['type'] != 'login': raise dash.exceptions.PreventUpdate

        translation = app.language_handler[language]

        # Load the hike list ui elements based on the data from the db
        hikes_info, widgets, traces = generate_hike_ui_elements_with_login(app, language)

        login_button_tooltip = app.language_handler[language]['login_logout_buttons']['logout' if 'user_id' in session else 'login']['tooltip']

        # Recover the username
        try:
            username = Users_table.get_username_from_user_id(session['user_id'])
        except NoUserIdInDB: raise dash.exceptions.PreventUpdate

        # Generate the container items for the magic link panel
        children = generate_magic_link_container_rows_from_db(
            app.language_handler[language]['magic_link_panel'],
            list(hikes_info.keys())
        )

        return (
            generate_leaflet_map_figure(),
            [login_success_notification(translation['notifications'])], 
            (username, username), (login_button_tooltip, login_button_tooltip),
            widgets, len(widgets), hikes_info, 
            traces,
            False, False,
            children
        )
    
    @app.callback(
        dash.Output('login-modal-id-input', 'value', allow_duplicate=True),
        dash.Output('login-modal-password-input', 'value', allow_duplicate=True),
        dash.Input('login-modal', 'opened'),
        prevent_initial_call=True
    )
    def exit_login_modal(is_open: bool) -> tuple[str, str]:
        r'''
        Callback used when the modal is closed. This clears the username and password fields when logging out.

        :param is_open: whether the login modal is open or not

        :returns: ('', '') in order to clear the two fields
        '''
        
        if not is_open: return '', ''
        else: raise dash.exceptions.PreventUpdate

    @app.callback(
        dash.Output('login-modal', 'opened', allow_duplicate=True),
        dash.Output({'type' : 'login-button', 'index' : dash.ALL}, 'children', allow_duplicate=True),
        dash.Output({'type' : 'login-button-tooltip', 'index' : dash.ALL}, 'label', allow_duplicate=True),

        dash.Output( 'map-polylines', 'children', allow_duplicate=True),

        dash.Output('hikelist-div', 'children', allow_duplicate=True),
        dash.Output('number-hikes', 'data',     allow_duplicate=True),

        dash.Output('hikes-info',                    'data', allow_duplicate=True),
        dash.Output('colorpicker-selected-id',       'data', allow_duplicate=True),
        dash.Output('selected-hike-props',           'data', allow_duplicate=True),
        dash.Output('selected-hike-data-for-plot',   'data', allow_duplicate=True),
        dash.Output('selected-hike-data-for-marker', 'data', allow_duplicate=True),

        dash.Output('map-div',                'style',             allow_duplicate=True),
        dash.Output('elevation-plot-stack',   'style',             allow_duplicate=True),

        dash.Output('notification-container', 'sendNotifications', allow_duplicate=True),

        dash.Output('magic-link-button', 'disabled', allow_duplicate=True),
        dash.Output('magic-link-container', 'children', allow_duplicate=True),

        dash.Input( {'type' : 'login-button', 'index' : dash.ALL}, 'n_clicks'),
        dash.State( 'login-modal', 'opened'),
        dash.State( 'language',    'data'),
        prevent_initial_call=True
    )
    def topbar_login_button(
            _, 
            opened   : bool, 
            language : LANGUAGE
        ) -> tuple[
            bool, 
            tuple[str, str] | tuple[dash.NoUpdate, dash.NoUpdate], 
            tuple[str, str] | tuple[dash.NoUpdate, dash.NoUpdate],

            list | dash.NoUpdate, 

            list | dash.NoUpdate, 
            int  | dash.NoUpdate, 

            dict[str, HikeInfo]      | dash.NoUpdate,
            str                      | dash.NoUpdate,
            HikeProps                | dash.NoUpdate,
            HikeDataForElevationPlot | dash.NoUpdate,
            HikeDataForMarker           | dash.NoUpdate,

            dict[str, str] | dash.NoUpdate,
            dict[str, str] | dash.NoUpdate,

            list[Notification] | dash.NoUpdate,

            typing.Literal[True],
            list | dash.NoUpdate
        ]:
        r'''
        Callback used when the login/logout button on the topbar is clicked.

        :param opened: whether the login modal is opened or not
        :param language: language of the UI
        '''

        # Handle logout button click
        if 'user_id' in session:

            session.clear()
            session['magic-link'] = False

            translation = app.language_handler[language]

            login_button_text    = translation['login_logout_buttons']['login']['text']
            login_button_tooltip = translation['login_logout_buttons']['login']['tooltip']

            traces         = []
            widgets        = []
            n_hikes        = 0
            hikes_info     = {}
            colorpicker_id = ''
            hike_props     = HikeProps(name='', color='')
            hike_data_ev   = HikeDataForElevationPlot(distances=[], elevations=[])
            hike_data_map  = HikeDataForMarker(latitudes=[], longitudes=[])
            
            return (
                False, 
                (login_button_text, login_button_text), 
                (login_button_tooltip, login_button_tooltip),
                traces, widgets, n_hikes,
                hikes_info, colorpicker_id, hike_props, hike_data_ev, hike_data_map,
                {'height' : '100%'}, {'display' : 'none'},
                [logout_success_notification(translation['notifications'])],
                True,
                []
            )

        # Handle login button click
        return (
            not opened, 
            (dash.no_update, dash.no_update), 
            (dash.no_update, dash.no_update), 
            dash.no_update, dash.no_update, dash.no_update, 
            dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update,
            dash.no_update, dash.no_update,
            dash.no_update,
            True,
            dash.no_update
        )

    return