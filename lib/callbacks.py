import dash
import pathlib
import plotly.graph_objects as     go
from   urllib.parse         import urlparse, parse_qs
from   flask                import session
from   plotly.colors        import qualitative

from   .lang                import LANGUAGE
from   .io                  import parse_uploaded_file
from   .components          import ui_layout, hikelist_element_layout
from   .components.map      import line_for_map
from   .database            import validate_credentials
from   .components          import (
    login_success_notification,
    login_username_fail_notification,
    login_password_fail_notification,
    logout_success_notification
)

COLOR_PALETTE = qualitative.Plotly

def register_callbacks(
        app              : dash.Dash, 
        token_db         : dict
    ) -> None:
    r'''
    Register all callbacks.

    :param app: dash application
    :param language_handler: object containing the default text for UI elements
    :param token_db: token used to set up the UI with a magic link
    '''
    
    #register_ui_init_callbacks(app, token_db)
    register_language_callacks(app)
    register_menubar_callbacks(app)
    register_topbar_callbacks(app)
    register_hike_drawer_callbacks(app)
    register_login_modal_callbacks(app)
    register_map_callbacks(app)

    return

def register_ui_init_callbacks(
        app: dash.Dash, token_db: dict
    ) -> None:
    r'''
    Register all callbacks that initialize the UI based on the input token.

    :param app: dash application
    :param token_db: token used to set up the UI with a magic link
    '''

    @app.callback(
        [
            dash.Output('content-display', 'children'),
            dash.Output('number_hikes', 'data')
        ],
        dash.Input('url', 'href'),
        dash.State('language', 'data')
    )
    def render_ui(url: str, language: LANGUAGE) -> tuple[dash.html.Div, int]:
        r'''
        Callback used at startup to define how the UI is rendered.

        :param url: url of the page
        '''

        parsed_url   = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        token_list   = query_params.get('token')

        '''
        if (
            token_list is None   or 
            len(token_list) > 1  or 
            len(token_list) == 0 or
            (token := token_list[0]) not in token_db
        ): 
        '''
            
        hikes_data = {}

        '''
        else:

            # Select the sub-sample of hikes provided by the token key
            hike_names = token_db[token]
            hikes_data = load_hikes_from_directory()
            hikes_data = {name : hikes_data[name] for name in hike_names}
        '''
        return dash.html.Div(ui_layout(app.language_handler, language)), len(hikes_data)
    
    return

def register_language_callacks(app: dash.Dash) -> None:
    r'''
    Register all callbacks that update the language of the UI

    :param app: dash application
    :param language_handler: object containing the default text for UI elements
    '''

    @app.callback(
        [
            dash.Output('language', 'data'),
            dash.Output('theme-toggle-tooltip', 'label'),
            dash.Output('hike-panel-button-tooltip', 'label'),
            dash.Output('hall-of-fame-button-tooltip', 'label'),
            dash.Output('hike-panel', 'title'),
            dash.Output({'type' : 'hikelist-hide-button-tooltip',  'index' : dash.ALL}, 'label'),
            dash.Output({'type' : 'hikelist-colorpicker-tooltip',  'index' : dash.ALL}, 'label'),
            dash.Output({'type' : 'hikelist-share-button-tooltip', 'index' : dash.ALL}, 'label'),
            dash.Output('upload-hike-button', 'children'),
            dash.Output('login-button', 'children'),
            dash.Output('login-button-tooltip', 'label'),
            dash.Output('logout-button-tooltip', 'label'),
            dash.Output('login-modal', 'title'),
            dash.Output('login-modal-id-input', 'label'),
            dash.Output('login-modal-id-input', 'placeholder'),
            dash.Output('login-modal-password-input', 'label'),
            dash.Output('login-modal-password-input', 'placeholder'),
            dash.Output('send-login-button', 'children'),
            dash.Output('login-success-notification', 'data'),
            dash.Output('login-username-fail-notification', 'data'),
            dash.Output('login-password-fail-notification', 'data'),
            dash.Output('logout-success-notification', 'data')
        ],
        dash.Input('language-dropdown', 'value'),
        dash.State('number_hikes', 'data'),
        prevent_initial_call=True,
    )
    def language_selection(lang: LANGUAGE, n_hikes: int) -> tuple[
        LANGUAGE,
        str, str, str, str, 
        list[str], list[str], list[str], tuple[str],
        str, str, str, 
        str, str, str, str, str, str,
        dict, dict, dict, dict
    ]:
        r'''
        Callback used when the language of the application is changed.

        :param value: new selected language
        :param n_hikes: total number of hike elements
        '''

        translation = app.language_handler[lang]

        login_sn    = login_success_notification(translation)
        login_ufn   = login_username_fail_notification(translation)
        login_pfn   = login_password_fail_notification(translation)
        logout_sn   = logout_success_notification(translation)

        return (
            lang,

            translation['topbar']['theme_switcher']['tooltip'],
            translation['menubar']['hike_panel_button']['tooltip'],
            translation['menubar']['hall_of_fame_button']['tooltip'],
            translation['hike_panel']['title'],

            [translation['hike_panel']['hide_button']['tooltip']]  * n_hikes,
            [translation['hike_panel']['colorpicker']['tooltip']]  * n_hikes,
            [translation['hike_panel']['share_button']['tooltip']] * n_hikes,
            (translation['hike_panel']['upload_button']['text'],),

            translation['topbar']['login_button']['text'],
            translation['topbar']['login_button']['tooltip'],
            translation['topbar']['logout_button']['tooltip'],

            translation['login_modal']['title']['text'],
            translation['login_modal']['user_id_input']['label'],
            translation['login_modal']['user_id_input']['placeholder'],
            translation['login_modal']['user_password_input']['label'],
            translation['login_modal']['user_password_input']['placeholder'],
            translation['login_modal']['send_login_button']['text'],

            login_sn,
            login_ufn,
            login_pfn,
            logout_sn
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
    ) -> tuple[
            list[dict[str, str]] | list[dash.NoUpdate], 
            go.Figure | dash.NoUpdate
    ]:
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
                'center' : {'lat' : info['lat'], 'lon' : info['lon']},
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
            dash.Output({'type' : 'hikelist-colorpicker-tooltip',  'index' : dash.ALL}, 'disabled'),
            dash.Output({'type' : 'hikelist-share-button-tooltip', 'index' : dash.ALL}, 'disabled'),
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
            tuple[list[bool], list[bool], list[bool], list[bool], list[bool], go.Figure] | 
            tuple[list[dash.NoUpdate], list[dash.NoUpdate], list[dash.NoUpdate], list[dash.NoUpdate], list[dash.NoUpdate], dash.NoUpdate]
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

        return output, output, output, output, output, map_figure

    @app.callback(
        [
            dash.Output('hikelist-div', 'children'),
            dash.Output('number_hikes', 'data'),
            dash.Output('hikes_info', 'data'),
            dash.Output('map', 'figure', allow_duplicate=True)
        ],
        dash.Input('upload-hike-button', 'contents'),
        dash.State('upload-hike-button', 'filename'),
        dash.State('hikelist-div', 'children'),
        dash.State('map', 'figure'),
        dash.State('language', 'data'),
        dash.State('hikes_info', 'data'),
        prevent_initial_call = True
    )
    def upload_hike(
        file_contents : list[str] | None, 
        filenames     : list[str], 
        hike_widgets  : list,
        map_dict      : dict,
        language      : LANGUAGE,
        hikes_info    : dict
    ) -> tuple[
            list | dash.NoUpdate, 
            int | dash.NoUpdate, 
            dict | dash.NoUpdate,
            go.Figure | dash.NoUpdate
        ]:

        if file_contents is None or len(file_contents) == 0: 
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update

        figure        = go.Figure(map_dict)

        language_dict = app.language_handler[language]['hike_panel']
        pos_init      = len(hike_widgets)

        new_hike_widgets = []
        for pos, (content, filename) in enumerate(zip(file_contents, filenames)):

            pos_absolute = pos_init + pos

            # Get the name of the file and parse its content
            filename, properties = parse_uploaded_file(content, filename)

            # None means the parsing failed
            if properties is None: continue

            hike_name            = pathlib.Path(filename).stem
            color                = COLOR_PALETTE[pos_absolute]

            # Create a hike widget in the hike list
            widget   = hikelist_element_layout(
                hike_name,
                color,
                pos_absolute,
                False if pos_absolute > 0 else True,
                language_dict
            )

            new_hike_widgets.append(widget)

            # Add a trace to the figure
            figure.add_trace(line_for_map(
                hike_name,
                properties['lon'],
                properties['lat'],
                color
            ))

            # Add hike information to the Store component
            hikes_info[hike_name] = {
                'lat'  : properties['center'][0],
                'lon'  : properties['center'][1],
                'zoom' : properties['zoom']
            }

        hike_widgets.extend(new_hike_widgets)

        return hike_widgets, len(hike_widgets), hikes_info, figure
    
    return

def register_topbar_callbacks(app: dash.Dash) -> None:
    '''
    Register all callbacks associated to widgets in the topbar.

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
            dash.Output('logout-button', 'style', allow_duplicate=True),
            dash.Output('login-button', 'style', allow_duplicate=True),
            dash.Output('notification-container', 'sendNotifications', allow_duplicate=True),
        ],
        dash.Input('logout-button', 'n_clicks'),
        dash.State('logout-success-notification', 'data'),
        prevent_initial_call=True
    )
    def logout_button(_, success_notification: dict) -> tuple[dict, dict, list[dict]]:
        r'''
        Callback used when the user clicks the logout button.
        '''

        session.clear()

        return {'display' : 'none'}, {'display' : 'flex'}, [success_notification], 
    
    return

def register_login_modal_callbacks(app: dash.Dash) -> None:
    r'''
    Register all callbacks associated to widgets in the login modal.

    :param app: dash application
    '''

    @app.callback(
        [
            dash.Output('login-modal', 'opened', allow_duplicate=True),
            dash.Output('notification-container', 'sendNotifications'),
            dash.Output('logout-button', 'style'),
            dash.Output('logout-button', 'children'),
            dash.Output('login-button', 'style'),
        ],
        dash.Input('send-login-button', 'n_clicks'),
        dash.State('login-modal-id-input', 'value'),
        dash.State('login-modal-password-input', 'value'),
        dash.State('login-success-notification', 'data'),
        dash.State('login-username-fail-notification', 'data'),
        dash.State('login-password-fail-notification', 'data'),
        prevent_initial_call=True
    )
    def secure_login(
        _, 
        username                   : str, 
        password                   : str,
        success_notification       : dict,
        username_fail_notification : dict,
        password_fail_notification : dict
        ) -> tuple[bool, list[dict] | dash.NoUpdate, dict, str | dash.NoUpdate, dict]:

        if password is None or username is None:
            return False, dash.no_update, {'display' : 'none'}, dash.no_update, {}

        res = validate_credentials(username, password)

        # Handle case if the username is wrong
        if res is None:
            return True, [username_fail_notification], {'display' : 'none'}, dash.no_update, {}
        
        # Check if the provided password matches the hash
        if not res:
            return True, [password_fail_notification], {'display' : 'none'}, dash.no_update, {}
        
        session['user_id'] = username

        # Otherwise, sends a login success notification
        return False, [success_notification], {'display' : 'flex'}, username, {'display' : 'none'}

    return

def register_map_callbacks(app: dash.Dash) -> None:
    r'''
    Register all callbacks associated to the map.

    :param app: dash application
    '''

    @app.callback(
        dash.Output('map', 'figure', allow_duplicate = True),
        dash.Input({'type' : 'map-style-button', 'index' : dash.ALL}, 'n_clicks'),
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
        figure.update_layout(mapbox = {'style' : clicked_index})

        return figure
    
    return