import os
import dash
import psycopg2
import plotly.graph_objects as     go
from   dash_iconify         import DashIconify
from   urllib.parse         import urlparse, parse_qs

from   .lang                import LanguageEnum, LanguageHandler
from   .io                  import load_hikes_from_directory
from   .components          import ui_layout
from   .database            import hash_password, compare_passwords

def register_callbacks(
        app              : dash.Dash, 
        language_handler : LanguageHandler,
        token_db         : dict
    ) -> None:
    r'''
    Register all callbacks.

    :param app: dash application
    :param language_handler: object containing the default text for UI elements
    :param token_db: token used to set up the UI with a magic link
    '''
    
    register_ui_init_callbacks(app, language_handler, token_db)
    register_language_callacks(app, language_handler)
    register_menubar_callbacks(app)
    register_hike_drawer_callbacks(app)
    register_login_modal_callbacks(app)
    register_map_callbacks(app)

    return

def register_ui_init_callbacks(
        app: dash.Dash, language_handler: LanguageHandler, token_db: dict
    ) -> None:
    r'''
    Register all callbacks that initialize the UI based on the input token.

    :param app: dash application
    :param language_handler: object containing the default text for UI elements
    :param token_db: token used to set up the UI with a magic link
    '''

    @app.callback(
        [
            dash.Output('content-display', 'children'),
            dash.Output('number_hikes', 'data')
        ],
        dash.Input('url', 'href')
    )
    def render_ui(url: str) -> tuple[dash.html.Div, int]:
        r'''
        Callback used at startup to define how the UI is rendered.

        :param url: url of the page
        '''

        parsed_url   = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        token_list   = query_params.get('token')

        if (
            token_list is None   or 
            len(token_list) > 1  or 
            len(token_list) == 0 or
            (token := token_list[0]) not in token_db
        ): 
            
            hikes_data = {}

        else:

            # Select the sub-sample of hikes provided by the token key
            hike_names = token_db[token]
            hikes_data = load_hikes_from_directory()
            hikes_data = {name : hikes_data[name] for name in hike_names}
            
        return dash.html.Div(ui_layout(hikes_data, language_handler)), len(hikes_data)
    
    return

def register_language_callacks(app: dash.Dash, language_handler: LanguageHandler) -> None:
    r'''
    Register all callbacks that update the language of the UI

    :param app: dash application
    :param language_handler: object containing the default text for UI elements
    '''

    @app.callback(
        [
            dash.Output('theme-toggle-tooltip', 'label'),
            dash.Output('hike-panel-button-tooltip', 'label'),
            dash.Output('hall-of-fame-button-tooltip', 'label'),
            dash.Output('hike-panel', 'title'),
            dash.Output({'type' : 'hikelist-hide-button-tooltip',  'index' : dash.ALL}, 'label'),
            dash.Output({'type' : 'hikelist-colorpicker-tooltip',  'index' : dash.ALL}, 'label'),
            dash.Output({'type' : 'hikelist-share-button-tooltip', 'index' : dash.ALL}, 'label'),
            dash.Output('login-button', 'children'),
            dash.Output('login-button-tooltip', 'label'),
            dash.Output('login-modal', 'title'),
            dash.Output('login-modal-id-input', 'label'),
            dash.Output('login-modal-id-input', 'placeholder'),
            dash.Output('login-modal-password-input', 'label'),
            dash.Output('login-modal-password-input', 'placeholder'),
            dash.Output('send-login-button', 'children')
        ],
        dash.Input('language-dropdown', 'value'),
        dash.State('number_hikes', 'data'),
        prevent_initial_call=True,
    )
    def language_selection(value: str, n_hikes: int) -> tuple[
        str, str, str, str, 
        list[str], list[str], list[str],
        str, str, str, str, str, str, str, str
    ]:
        r'''
        Callback used when the language of the application is changed.

        :param value: new selected language
        :param n_hikes: total number of hike elements
        '''

        # Value in the dropdown is a string so we parse it to the right type
        lang = LanguageEnum.map_string_code_to_language(value)

        # Update the language of the language handler object
        language_handler.language = lang

        return (
            language_handler['topbar']['theme_switcher']['tooltip'],
            language_handler['menubar']['hike_panel_button']['tooltip'],
            language_handler['menubar']['hall_of_fame_button']['tooltip'],
            language_handler['hike_panel']['title'],

            [language_handler['hike_panel']['hide_button']['tooltip']]  * n_hikes,
            [language_handler['hike_panel']['colorpicker']['tooltip']]  * n_hikes,
            [language_handler['hike_panel']['share_button']['tooltip']] * n_hikes,

            language_handler['topbar']['login_button']['text'],
            language_handler['topbar']['login_button']['tooltip'],
            language_handler['login_modal']['title']['text'],
            language_handler['login_modal']['user_id_input']['label'],
            language_handler['login_modal']['user_id_input']['placeholder'],
            language_handler['login_modal']['user_password_input']['label'],
            language_handler['login_modal']['user_password_input']['placeholder'],
            language_handler['login_modal']['send_login_button']['text'],
        )
    
    return

def register_menubar_callbacks(app: dash.Dash) -> None:
    r'''
    Register all callbacks associated to widgets in the menubar.

    :param app: dash application
    '''

    @app.callback(
        dash.Output('hike-panel', 'opened'),
        dash.Input('hike-panel-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def hike_panel_button(_: int) -> bool:
        r'''Callback used when the hike panel button is clicked.'''

        return True
    
    return

def register_hike_drawer_callbacks(app: dash.Dash) -> None:
    r'''
    Register all callbacks associated to widgets in the hike drawer.

    :param app: dash application
    '''

    @app.callback(
        [
            dash.Output({'type' : 'hikelist-button', 'index' : dash.ALL}, 'style'),
            dash.Output('map', 'figure')
        ],
        dash.Input( {'type' : 'hikelist-button', 'index' : dash.ALL}, 'n_clicks'),
        dash.State('number_hikes', 'data'),
        dash.State('hikes_info', 'data'),
        dash.State('map', 'figure'),
        prevent_initial_call = True
    )
    def hike_button(
        _, n_hikes: int, hikes_info: dict, map_dict: dict
    ) -> tuple[list[dict[str, str]] | list[dash.NoUpdate], go.Figure | dash.NoUpdate]:
        r'''
        Callback used when a hike is selected in the hike list.

        :param n_hikes: total number of hike list components
        :param hikes_info: hike properties containing information such as center and zoom level
        :param map_dict: current state of the map plot 
        '''

        ctx = dash.callback_context

        if ctx is None or not ctx.triggered: return [dash.no_update] * n_hikes, dash.no_update

        styles = [{}] * n_hikes

        # Extract the ID of the clicked button
        clicked_index = ctx.triggered_id['index'] # type: ignore

        styles[clicked_index] = {'backgroundColor': 'var(--custom-theme-color)', 'color' : 'white'}

        # Get distances and elevations for the given hike
        name = list(hikes_info.keys())[clicked_index]
        info = hikes_info[name]

        map_figure = go.Figure(map_dict)

        map_figure.update_layout(
            mapbox= {
                'center' : {'lat' : info['center'][0], 'lon' : info['center'][1]},
                'zoom'   : info['zoom']
            }
        )

        return styles, map_figure
    
    @app.callback(
        dash.Output('map', 'figure', allow_duplicate=True),
        dash.Input({'type' : 'hikelist-colorpicker', 'index' : dash.ALL}, 'value'),
        dash.State('map', 'figure'),
        prevent_initial_call=True
    )
    def colorpicker(colors: str, map_dict: dict) -> go.Figure | dash.NoUpdate:
        '''
        Callback called whenever the given colorpicker is clicked.
        
        :param colors: colors selected by the colorpickers
        :param map_dict: current state of the map plot 
        '''

        ctx = dash.callback_context

        if ctx is None or not ctx.triggered: return dash.no_update

        # Extract the ID of the clicked button
        clicked_index = ctx.triggered_id['index'] # type: ignore

        map_figure = go.Figure(map_dict)
        map_figure.update_traces(
            line     = {'color' : colors[clicked_index]},
            selector = clicked_index + 1
        )

        return map_figure
    
    @app.callback(
        [
            dash.Output({'type' : 'hikelist-button',       'index' : dash.ALL}, 'disabled'),
            dash.Output({'type' : 'hikelist-colorpicker',  'index' : dash.ALL}, 'disabled'),
            dash.Output({'type' : 'hikelist-share-button', 'index' : dash.ALL}, 'disabled'),
            dash.Output('map', 'figure', allow_duplicate=True)
        ],
        dash.Input({'type' : 'hikelist-hide-button', 'index' : dash.ALL}, 'checked'),
        dash.State('map', 'figure'),
        dash.State({'type' : 'hikelist-colorpicker', 'index' : dash.ALL}, 'value'),
        dash.State('number_hikes', 'data'),
        prevent_initial_call = True
    )
    def hide_button(
        checked_list: list[bool], map_dict: dict, colors: list[str], number_hikes: int
    ) -> (
            tuple[list[bool], list[bool], list[bool], go.Figure] | 
            tuple[list[dash.NoUpdate], list[dash.NoUpdate], list[dash.NoUpdate], dash.NoUpdate]
        ):
        r'''
        Callback used when the hide button is toggled.

        :param checked_list: whether the hide buttons are checked
        :param map_dict: current layout for the map
        :param colors: current colors for each colorpicker
        :param number_hikes: total number of hike elements
        '''

        ctx = dash.callback_context

        if ctx is None or not ctx.triggered: 
            return (
                [dash.no_update] * number_hikes,
                [dash.no_update] * number_hikes,
                [dash.no_update] * number_hikes,
                dash.no_update
            )

        # Extract the ID of the clicked button
        clicked_index = ctx.triggered_id['index'] # type: ignore
        checked       = checked_list[clicked_index]

        map_figure = go.Figure(map_dict)
        map_figure.update_traces(
            line     = {
                'color' : 'rgba(0, 0, 0, 0)' if not checked else colors[clicked_index]
            },
            selector = clicked_index + 1
        )

        output                = [not i for i in checked_list]
        output[clicked_index] = not checked

        return output, output, output, map_figure

    return

def register_login_modal_callbacks(app: dash.Dash) -> None:
    r'''
    Register all callbacks associated to widgets in the login modal.

    :param app: dash application
    '''

    @app.callback(
        dash.Output('login-modal', 'opened'),
        dash.Input('login-button', 'n_clicks'),
        dash.State('login-modal', 'opened'),
        prevent_initial_call=True
    )
    def topbar_login_button(_, opened: bool) -> bool:
        r'''
        Callback used when the login button on the topbar is clicked.

        :param opened: whether the login modal is opened or not
        '''
        
        return not opened

    @app.callback(
        [
            dash.Output('login-modal', 'opened', allow_duplicate=True),
            dash.Output('notification-container', 'sendNotifications')
        ],
        dash.Input('send-login-button', 'n_clicks'),
        dash.State('login-modal-id-input', 'value'),
        dash.State('login-modal-password-input', 'value'),
        prevent_initial_call=True
    )
    def modal_login_button(_, username: str, password: str) -> tuple[bool, list[dict] | dash.NoUpdate]:

        if password is None or username is None:
            return False, dash.no_update

        hash = hash_password(password)
        print('from me', username, password, hash)

        conn = psycopg2.connect(
            dbname   = os.getenv('DB_NAME'),
            host     = os.getenv('DB_HOST'),
            port     = os.getenv('DB_PORT'),
            user     = os.getenv('DB_USER'),
            password = os.getenv('DB_PASSWORD')
        )

        cursor = conn.cursor()
        
        cursor.execute(f"SELECT password_hash FROM users WHERE username = '{username}'")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        # Handle case if the username is wrong
        if len(rows) == 0:

            return True, [{
                'title'     : 'Error',
                'position'  : 'top-center',
                'action'    : 'show',
                'message'   : 'Wrong username.',
                'color'     : 'red',
                'autoClose' : 4000,
                'icon'      : DashIconify(icon='si:error-duotone')
            }]
        
        # Check if the provided password matches the hash
        hash = rows[0][0]
        if not compare_passwords(password, hash):

            return True, [{
                'title'     : 'Error',
                'position'  : 'top-center',
                'action'    : 'show',
                'message'   : 'Invalid password.',
                'color'     : 'red',
                'autoClose' : 4000,
                'icon'      : DashIconify(icon='si:error-duotone')
            }]

        # Otherwise, sends a login success notification
        return False, [{
                'title'     : 'Login successful !',
                'position'  : 'top-center',
                'action'    : 'show',
                #'message'   : f'Welcome {username}',
                'color'     : 'green',
                'autoClose' : 4000,
                'icon'      : DashIconify(icon='icon-park-outline:success')
            }]

    return

def register_map_callbacks(app: dash.Dash) -> None:
    r'''
    Register all callbacks associated to the map.

    :param app: dash application
    '''

    @app.callback(
        dash.Output('map', 'figure', allow_duplicate = True),
        dash.Input({'type' : 'map-style-button',    'index' : dash.ALL}, 'n_clicks'),
        dash.State('map', 'figure'),
        prevent_initial_call = True
    )
    def map_style_change_from_button(_, map_dict: go.Figure) -> go.Figure | dash.NoUpdate:
        r'''
        Callback used whenever the user clicks one of the buttons allowing to change the style of the map.

        :param map_dict: dictionary containing the current design of the map
        '''

        ctx = dash.callback_context# Extract the ID of the clicked button

        if ctx is None or not ctx.triggered: return dash.no_update

        clicked_index = ctx.triggered_id['index'] # type: ignore

        figure = go.Figure(map_dict)
        figure.update_layout(
            mapbox = {'style' : clicked_index}
        )

        return figure
    
    return