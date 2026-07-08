import dash
import pathlib
import dash_mantine_components as     dmc
import plotly.graph_objects    as     go
import dash_leaflet            as     dl
import numpy                   as     np
from   urllib.parse            import urlparse, parse_qs
from   flask                   import session
from   plotly.colors           import qualitative
from   dash_iconify            import DashIconify

from   .lang                   import LANGUAGE
from   .io                     import parse_uploaded_file
from   .components             import hikelist_element_layout, language_element
from   .misc                   import check_if_hike_is_loaded
from   .database               import (
    Hikes_table,
    Users_table,
    Magic_links_table,
    validate_credentials, 
    execute_get_query,
)

from   .components             import (
    login_success_notification,
    login_username_fail_notification,
    login_password_fail_notification,
    logout_success_notification,
    hike_upload_success_notification,
    hike_upload_format_fail_notification,
    hike_upload_already_there_fail_notification
)

COLOR_PALETTE = qualitative.Plotly

def register_callbacks(app : dash.Dash) -> None:
    r'''
    Register all callbacks.

    :param app: dash application
    '''
    
    register_ui_init_callbacks(app)
    register_login_modal_callbacks(app)
    register_menubar_callbacks(app)
    register_hike_drawer_callbacks(app)
    register_upload_hike_callbacks(app)
    register_magic_link_modal_callbacks(app)
    register_language_callacks(app)
    register_login_buttons_callbacks(app)
    register_burger_callbacks(app)
    register_keydown_callbacks(app)

    return

def register_keydown_callbacks(app: dash.Dash) -> None:
    
    @app.callback(
        dash.Output('hike-panel', 'opened', allow_duplicate=True),
        dash.Input('keyboard', 'n_keydowns'),
        dash.State('keyboard', 'keydown'),
        dash.State('hike-panel', 'opened'), 
        prevent_initial_call=True
    )
    def register_keydown(_, keydown: dict, is_hike_panel_open: bool) -> bool:

        if keydown['key'] == 'l' and keydown['altKey']:
            return not is_hike_panel_open
        
        raise dash.exceptions.PreventUpdate

def register_burger_callbacks(app: dash.Dash) -> None:
    r'''
    Register all callbacks that define the behaviour of the burger component in the topbar.

    :param app: dash application
    '''

    @app.callback(
        dash.Output("appshell", "navbar"),
        dash.Input("burger", "opened"),
        dash.State("appshell", "navbar"),
    )
    def toggle_navbar(opened, navbar):

        navbar["collapsed"] = {"mobile": not opened, 'desktop' : not opened}
        return navbar

    return

def register_ui_init_callbacks(app: dash.Dash) -> None:
    r'''
    Register all callbacks that initialize the UI based on the input token.

    :param app: dash application
    '''

    @app.callback(
        dash.Output({'type' : 'login-button', 'index' : dash.ALL}, 'style', allow_duplicate=True),

        dash.Output('hike_names_list',   'data',     allow_duplicate=True),
        dash.Output('hikelist-div',      'children', allow_duplicate=True),
        dash.Output('number_hikes',      'data',     allow_duplicate=True),
        dash.Output('hikes_info',        'data',     allow_duplicate=True),

        dash.Output('map-polylines',     'children', allow_duplicate=True),
        dash.Output('elevation-plot',    'style',    allow_duplicate=True),

        dash.Output('upload-hike-button',     'style',             allow_duplicate=True),
        dash.Output('notification-container', 'sendNotifications', allow_duplicate=True),

        dash.Output('base-url', 'data'),

        dash.Input('url', 'href'),
        dash.State('language', 'data'),
        dash.State('wrong-magic-link-notification', 'data'),

        prevent_initial_call = True
    )
    def render_ui(
            url          : str, 
            language     : LANGUAGE,
            notification : dict
        ) -> tuple[
            tuple[dict, dict] | tuple[dash.NoUpdate, dash.NoUpdate],
            list[str]         | dash.NoUpdate, 
            list              | dash.NoUpdate, 
            int               | dash.NoUpdate, 
            dict              | dash.NoUpdate, 
            list[dl.Polyline] | dash.NoUpdate, 
            dict[str, str]    | dash.NoUpdate,
            dict[str, str]    | dash.NoUpdate, 
            list[dict]        | dash.NoUpdate,
            str
        ]:
        r'''
        Callback used at startup to define how the UI is rendered.

        :param url: url of the page
        :param language: selected language
        :param notification: notification shown when the magic link is wrong
        '''

        parsed_url   = urlparse(url)
        base_url     = parsed_url.scheme + '://' + parsed_url.netloc
        query_params = parse_qs(parsed_url.query)
        token_list   = query_params.get('token')

        # Case without a magic link
        if (token_list is None or len(token_list) != 1):

            ui_elements = handle_without_magic_link(language)

            return (
                *ui_elements, dash.no_update, {}, 
                dash.no_update,
                base_url
            )
    
        # Case with a magic link. Note the following when opening with a magic link:
        # - login and logout buttons are disabled
        # - upload hike button is disabled
        # - share hike buttons are disabled
        ui_elements = handle_with_magic_link(token_list[0], language)

        # Magic link incorrect
        if ui_elements is None: 
            
            return (
                (dash.no_update, dash.no_update), 
                dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                dash.no_update,  dash.no_update,
                dash.no_update, [notification], 
                base_url
            )

        # Magic link is correct
        return (
            ({'display' : 'none'}, {'display' : 'none'}), 
            *ui_elements, {'display' : 'flex'},
            dash.no_update, dash.no_update,
            base_url
        )
        
    def handle_with_magic_link(
            magic_link : str, 
            language   : LANGUAGE
        ) -> tuple[list[str], list, int, dict, list[dl.Polyline]] | None:
        '''
        Handle the rendering of the UI elements when the user is connecting with a magic link.

        :param magic_link: magic link provided in the url
        :param language: selected language

        :returns:
            - list of hike names
            - list of hike element widgets
            - number of hikes
            - dictionary with hike names as keys and dictionaries with hike information as values
            - list of Polylines object to draw on the map (hike paths)
        '''

        hike_id = Magic_links_table.get_hike_id_from_magic_link(magic_link)

        if hike_id is None: return
        
        # Query hikes database associated to the user
        hike_properties = execute_get_query(f'''
            SELECT name, latitude, longitude, center_lat, center_lon, zoom, distances, elevations
            FROM hikes
            WHERE id = {hike_id};
        ''')

        # Build the dictionary with hike properties
        property_dict = {}
        hike_names    = []

        for hike in hike_properties:

            hike_names.append(hike[0])

            property_dict[hike[0]]               = {}
            property_dict[hike[0]]['lat']        = hike[1]
            property_dict[hike[0]]['lon']        = hike[2]
            property_dict[hike[0]]['center']     = (hike[3], hike[4])
            property_dict[hike[0]]['zoom']       = hike[5]
            property_dict[hike[0]]['distances']  = hike[6]
            property_dict[hike[0]]['elevations'] = hike[7]

        ui_elements = update_ui_after_multiple_hike_loads(
            app, property_dict, [],
            language, {},
            magic_link_state = True
        )

        # Create a new figure and update all ui elements related to hikes
        return hike_names, *ui_elements

    def handle_without_magic_link(language: LANGUAGE
    ) -> tuple[tuple[dict[str, str], dict[str, str]], list[str], list, int, dict, list[dl.Polyline]]:
        '''
        Handle the rendering of the UI elements when the user is not connecting with a magic link.

        :param language: selected language

        :returns:
            - two dictionaries with the style for the login buttons
            - text for the login/logout button if user is connected
            - list of hike names
            - list of hike widgets
            - number of loaded hikes
            - dictionary with information for each hike
            - list of Polylines object to draw on the map (hike paths)
        '''

        # User session still active in the cookies
        if 'user_id' in session:

            username = Users_table.get_username_from_user_id(session['user_id'])

            # All ui elements associated to the hikes
            ui_elements = generate_hike_ui_elements_after_login(app, language, magic_link_state = False)

            return (
                ({'display' : 'none'}, {'display' : 'none'}),
                *ui_elements
            )

        # User session not active in the cookies
        return (
            ({'display' : 'flex'}, {'display' : 'flex'}),
            [], [], 0, {}, []
        )

    return

def register_language_callacks(app: dash.Dash) -> None:
    r'''
    Register all callbacks that update the language of the UI

    :param app: dash application
    :param language_handler: object containing the default text for UI elements
    '''

    @app.callback(
        dash.Output('language', 'data', allow_duplicate=True),

        dash.Output('theme-toggle-tooltip', 'label'),
        dash.Output('hike-panel-button', 'children'),
        dash.Output('hike-panel-button-tooltip', 'label'),
        dash.Output('hall-of-fame-button', 'children'),
        dash.Output('hall-of-fame-button-tooltip', 'label'),
        dash.Output('hike-panel', 'title'),

        dash.Output({'type' : 'hikelist-hide-button-tooltip',  'index' : dash.ALL}, 'label'),
        dash.Output({'type' : 'hikelist-colorpicker-tooltip',  'index' : dash.ALL}, 'label'),
        dash.Output({'type' : 'hikelist-share-button-tooltip', 'index' : dash.ALL}, 'label'),
        dash.Output('upload-hike-button', 'children'),

        dash.Output({'type' : 'login-button', 'index' : dash.ALL}, 'children', allow_duplicate=True),
        dash.Output({'type' : 'login-button-tooltip', 'index' : dash.ALL}, 'label', allow_duplicate=True),

        dash.Output('login-modal', 'title'),
        dash.Output('login-modal-id-input', 'label'),
        dash.Output('login-modal-id-input', 'placeholder'),
        dash.Output('login-modal-password-input', 'label'),
        dash.Output('login-modal-password-input', 'placeholder'),
        dash.Output('send-login-button', 'children'),

        dash.Output('login-success-notification', 'data'),
        dash.Output('login-username-fail-notification', 'data'),
        dash.Output('login-password-fail-notification', 'data'),
        dash.Output('logout-success-notification', 'data'),

        dash.Output({'type' : 'language-dropdown', 'index' : dash.ALL}, 'children', allow_duplicate=True),
        dash.Output('magic-link-modal-text', 'children'),
        dash.Output('magic-link-modal', 'title'),
  
        dash.Input({'type': 'language-button', 'index': dash.ALL}, 'n_clicks'),
        dash.State('number_hikes', 'data'),

        prevent_initial_call=True,
    )
    def language_selection(n_clicks, n_hikes: int) -> tuple[
        str, 
        str, str, str, str, str, str,
        list[str], list[str], list[str], tuple[str],
        tuple[str, dash.NoUpdate] | tuple[dash.NoUpdate, dash.NoUpdate], tuple[str, str],
        str, str, str, str, str, str,
        dict, dict, dict, dict, 
        tuple[list, list],
        str, str
    ]:
        r'''
        Callback used when the language of the application is changed.

        :param n_clicks: which language was selected
        :param n_hikes: total number of hike elements
        '''

        if all(i is not None for i in n_clicks): raise dash.exceptions.PreventUpdate

        ctx = dash.callback_context

        if ctx is None or not ctx.triggered: raise dash.exceptions.PreventUpdate

        triggered_id = ctx.triggered_id

        if not isinstance(triggered_id, dict): raise dash.exceptions.PreventUpdate

        lang : LANGUAGE = triggered_id['index'].split('-')[-1]
        translation     = app.language_handler[lang]

        login_sn    = login_success_notification(translation)
        login_ufn   = login_username_fail_notification(translation)
        login_pfn   = login_password_fail_notification(translation)
        logout_sn   = logout_success_notification(translation)

        login_button_text    = translation['login_logout_buttons']['login']['text'] if 'user_id' not in session else dash.no_update
        login_button_tooltip = translation['login_logout_buttons']['logout' if 'user_id' in session else 'login']['tooltip']
        
        language_dropdown = [
            language_element(
                triggered_id['index'],
                app.language_handler.map_language_to_dropdown_text(selected_lang),
                selected_lang,
                selected_lang == lang
            )
            for selected_lang in app.language_handler.languages
        ]

        return (
            lang,
            translation['topbar']['theme_switcher']['tooltip'],
            translation['menubar']['hike_panel_button']['text'],
            translation['menubar']['hike_panel_button']['tooltip'],
            translation['menubar']['hall_of_fame_button']['text'],
            translation['menubar']['hall_of_fame_button']['tooltip'],
            translation['hike_panel']['title'],

            [translation['hike_panel']['hide_button']['tooltip']]  * n_hikes,
            [translation['hike_panel']['colorpicker']['tooltip']]  * n_hikes,
            [translation['hike_panel']['share_button']['tooltip']] * n_hikes,
            (translation['hike_panel']['upload_button']['text'],),

            (login_button_text, login_button_text),
            (login_button_tooltip, login_button_tooltip),

            translation['login_modal']['title'],
            translation['login_modal']['user_id_input']['label'],
            translation['login_modal']['user_id_input']['placeholder'],
            translation['login_modal']['user_password_input']['label'],
            translation['login_modal']['user_password_input']['placeholder'],
            translation['login_modal']['send_login_button']['text'],

            login_sn,
            login_ufn,
            login_pfn,
            logout_sn,

            (language_dropdown, language_dropdown),

            translation['magic_link_modal']['text'],
            translation['magic_link_modal']['title']
        )
    
    return

def register_menubar_callbacks(app: dash.Dash) -> None:
    r'''
    Register all callbacks associated to widgets in the menubar.

    :param app: dash application
    '''

    @app.callback(
        dash.Output('hike-panel', 'opened', allow_duplicate=True),
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
        dash.Output({'type' : 'hikelist-button', 'index' : dash.ALL}, 'style'),
        dash.Output('map', 'center'),
        dash.Output("burger", "opened"),
        dash.Output('hike-panel', 'opened', allow_duplicate=True),
        dash.Output('elevation-plot', 'data'),
         dash.Output('elevation-plot', 'yAxisProps'),
        #dash.Output('map', 'zoom'),

        dash.Input( {'type' : 'hikelist-button', 'index' : dash.ALL}, 'n_clicks'),
        dash.State('number_hikes', 'data'),
        dash.State('hikes_info', 'data'),
        dash.State('hike_names_list', 'data'),

        prevent_initial_call = True
    )
    def hike_button(
        _, n_hikes: int, hikes_info: dict, hike_names: list[str]
    ) -> tuple[list[dict[str, str]], tuple[float, float], bool, bool, list[dict], dict]:
        r'''
        Callback used when a hike is selected in the hike list.

        :param n_hikes: total number of hike list components
        :param hikes_info: hike properties containing information such as center and zoom level
        :parma hike_names_list: list containing the name of the hikes as they appear in the hike list
        '''

        ctx = dash.callback_context

        if ctx is None or not ctx.triggered: raise dash.exceptions.PreventUpdate

        styles = [{}] * n_hikes

        # Extract the ID of the clicked button
        clicked_index = ctx.triggered_id['index'] # type: ignore

        styles[clicked_index] = {'backgroundColor': 'var(--custom-theme-color)', 'color' : 'white'}

        # Get distances and elevations for the given hike
        name = hike_names[clicked_index]
        info = hikes_info[name]

        elevation_data = [{'x' : d, 'y' : e} for d, e in zip(info['distances'], info['elevations'])]

        return (
            styles, (info['lat'], info['lon']), 
            False, False,# info['zoom']
            elevation_data, {'domain' : [np.min(info['elevations']), np.max(info['elevations'])]}
        )
    
    @app.callback(
        dash.Output({'type' : 'map-trace', 'index' : dash.ALL}, 'pathOptions', allow_duplicate=True),
        dash.Input({'type' : 'hikelist-colorpicker', 'index' : dash.ALL}, 'value'),
        prevent_initial_call=True
    )
    def colorpicker(colors: list[str]) -> list[dict]:
        '''
        Callback called whenever the given colorpicker is clicked.
        
        :param colors: colors selected by the colorpickers
        '''

        from .components.map import generate_layer_control

        ctx = dash.callback_context

        if ctx is None or not ctx.triggered: raise dash.exceptions.PreventUpdate

        return [{'color' : color} for color in colors]
    
    @app.callback(
        dash.Output({'type' : 'hikelist-button',       'index' : dash.ALL}, 'disabled'),
        dash.Output({'type' : 'hikelist-colorpicker',  'index' : dash.ALL}, 'disabled'),
        dash.Output({'type' : 'hikelist-share-button', 'index' : dash.ALL}, 'disabled'),
        dash.Output({'type' : 'hikelist-colorpicker-tooltip',  'index' : dash.ALL}, 'disabled'),
        dash.Output({'type' : 'hikelist-share-button-tooltip', 'index' : dash.ALL}, 'disabled'),
        dash.Output({'type' : 'map-trace', 'index' : dash.ALL}, 'pathOptions', allow_duplicate=True),

        dash.Input({'type' : 'hikelist-hide-button', 'index' : dash.ALL}, 'checked'),
        dash.State({'type' : 'hikelist-colorpicker', 'index' : dash.ALL}, 'value'),
        dash.State('number_hikes', 'data'),

        prevent_initial_call = True
    )
    def hide_button(
        checked_list: list[bool], colors: list[str], number_hikes: int
    ) -> tuple[list[bool], list[bool], list[bool], list[bool], list[bool], list[dict]]:
        r'''
        Callback used when the hide button is toggled.

        :param checked_list: whether the hide buttons are checked
        :param colors: current colors for each colorpicker
        :param number_hikes: total number of hike elements
        '''

        ctx = dash.callback_context

        if ctx is None or not ctx.triggered: raise dash.exceptions.PreventUpdate

        # Extract the ID of the clicked button
        clicked_index = ctx.triggered_id['index'] # type: ignore
        checked       = checked_list[clicked_index]

        output                = [not i for i in checked_list]
        output[clicked_index] = not checked

        # Change disabled hikes color to transparent
        hike_colors = [{'color' : color if check else 'rgba(0, 0, 0, 0)'} for color, check in zip(colors, checked_list)]

        return output, output, output, output, output, hike_colors
    
    @app.callback(
        dash.Output('magic-link-modal', 'opened'),
        dash.Output('magic-link-copy-button', 'value'),
        dash.Output('magic-link-copy-button', 'children'),
        #dash.Output('magic-link-copy-button-tooltip', 'label'),
        dash.Input({'type' : 'hikelist-share-button', 'index' : dash.ALL}, 'n_clicks'),
        dash.State('hike_names_list', 'data'),
        dash.State('base-url', 'data'),
        prevent_initial_call = True
    )
    def share_hike(
            n_clicks   : list[int | None], 
            hike_names : list[str],
            base_url   : str
        ) -> tuple[bool, str, str]:
        r'''
        Callback used when any of the share buttons is clicked.
        
        :param n_clicks: number of clicks in each share button
        :param hike_names: name of each hike that is loaded
        :param base_url: base url at which the application is accessible 
        '''

        if all(n is None for n in n_clicks): raise dash.exceptions.PreventUpdate

        ctx          = dash.callback_context

        if ctx is None or not ctx.triggered: raise dash.exceptions.PreventUpdate

        triggered_id = ctx.triggered_id
        hike_name    = hike_names[triggered_id['index']] # type: ignore
        hike_id      = Hikes_table.get_hike_id_from_user_id_and_hike_name(
            session['user_id'], hike_name
        )

        if hike_id is None: raise dash.exceptions.PreventUpdate
        
        magic_link_id = Magic_links_table.get_magic_link_from_hike_id(hike_id)

        # If no magic link, we create it
        if magic_link_id is None: 
            Magic_links_table.insert_magic_link_into_db(hike_id)

        # Retrieve the magic link
        magic_link_id = Magic_links_table.get_magic_link_from_hike_id(hike_id)

        magic_link = f'{base_url}?token={magic_link_id}'

        return True, magic_link, magic_link
    
    return

def register_upload_hike_callbacks(app: dash.Dash) -> None:
    r'''All callbacks associated to uploading hikes.'''

    @app.callback(
        dash.Output('hike_names_list', 'data'),
        dash.Output('hikelist-div', 'children'),
        dash.Output('number_hikes', 'data'),
        dash.Output('hikes_info', 'data'),
        dash.Output('map-polylines', 'children', allow_duplicate=True),
        dash.Output('notification-container', 'sendNotifications', allow_duplicate=True),
        
        dash.Input('upload-hike-button', 'contents'),
        dash.State('upload-hike-button', 'filename'),
        dash.State('hikelist-div', 'children'),
        dash.State('map-polylines', 'children'),
        dash.State('language', 'data'),
        dash.State('hikes_info', 'data'),

        prevent_initial_call = True
    )
    def upload_hike(
        file_contents : list[str] | None, 
        filenames     : list[str], 
        hike_widgets  : list,
        map_polylines : list[dl.LayerGroup],
        language      : LANGUAGE,
        hikes_info    : dict
    ) -> (tuple[list, list, int, dict, go.Figure, list[dict]] |
          tuple[list, dash.NoUpdate, dash.NoUpdate, dash.NoUpdate, list, list[dict]]):

        ui_elements = (dash.no_update, dash.no_update, dash.no_update, [])

        if file_contents is None or len(file_contents) == 0: raise dash.exceptions.PreventUpdate
        
        # Default notification is success
        notification = hike_upload_success_notification(app.language_handler[language])

        # List of hike names updated as we load the new hikes below
        hike_names = list(hikes_info.keys())

        # Extract the properties of the loaded hikes
        hike_properties = {}

        for content, filename in zip(file_contents, filenames):

            filename, properties  = parse_uploaded_file(content, filename)

            # None means the parsing failed
            if properties is None: 
                
                notification = hike_upload_format_fail_notification(app.language_handler[language])
                notification['message'] += filename
                break

            hike_name = pathlib.Path(filename).stem

            # If the hike is loaded, we do not load any hikes. Users must only provide files that are not loaded yet
            if check_if_hike_is_loaded(hike_name, hike_names):

                notification = hike_upload_already_there_fail_notification(app.language_handler[language])
                notification['message'] += filename
                break
            
            else: hike_names.append(hike_name)

            hike_properties[hike_name] = properties

        else:

            # If logged in, we send hikes to the db
            if 'user_id' in session: 
                Hikes_table.insert_hikes_into_db(session['user_id'], hike_properties)

            ui_elements = update_ui_after_multiple_hike_loads(
                app, 
                hike_properties,
                hike_widgets,
                language,
                hikes_info
            )

        return (
            hike_names, 
            *ui_elements[:-1], 
            map_polylines + ui_elements[-1], 
            [notification] # pyright: ignore[reportReturnType]
        )

def register_login_buttons_callbacks(app: dash.Dash) -> None:
    '''
    Register all callbacks associated to widgets in the topbar.

    :param app: dash application
    '''

    @app.callback(
        dash.Output('login-modal', 'opened', allow_duplicate=True),
        dash.Output({'type' : 'login-button', 'index' : dash.ALL}, 'children', allow_duplicate=True),
        dash.Output({'type' : 'login-button-tooltip', 'index' : dash.ALL}, 'label', allow_duplicate=True),

        dash.Output( 'map-polylines', 'children', allow_duplicate=True),

        dash.Output('hike_names_list',   'data',     allow_duplicate=True),
        dash.Output('hikelist-div',      'children', allow_duplicate=True),
        dash.Output('number_hikes',      'data',     allow_duplicate=True),
        dash.Output('hikes_info',        'data',     allow_duplicate=True),

        dash.Output('elevation-plot', 'style', allow_duplicate=True),

        dash.Input( {'type' : 'login-button', 'index' : dash.ALL}, 'n_clicks'),
        dash.State( 'login-modal',  'opened'),
        dash.State( 'language',     'data'),
        prevent_initial_call=True
    )
    def topbar_login_button(
            _, 
            opened   : bool, 
            language : LANGUAGE
        ) -> tuple[
            bool, 
            tuple[str, DashIconify] | tuple[dash.NoUpdate, dash.NoUpdate], 
            tuple[str, str] | tuple[dash.NoUpdate, dash.NoUpdate],

            list | dash.NoUpdate, 

            list | dash.NoUpdate, 
            list | dash.NoUpdate, 
            int  | dash.NoUpdate, 
            dict | dash.NoUpdate,

            dict[str, str] | dash.NoUpdate
        ]:
        r'''
        Callback used when the login/logout button on the topbar is clicked.

        :param opened: whether the login modal is opened or not
        :param language: language of the UI
        '''

        # Handle logout button click
        if 'user_id' in session:

            session.clear()

            translation = app.language_handler[language]

            login_button_text    = translation['login_logout_buttons']['login']['text']
            login_button_tooltip = translation['login_logout_buttons']['login']['tooltip']

            return (
                False, 
                (login_button_text, login_button_text), 
                (login_button_tooltip, login_button_tooltip),
                [],
                [], [], 0, {}, 
                {'display' : 'none'}
            )

        # Handle login button click
        return (
            not opened, 
            (dash.no_update, dash.no_update), (dash.no_update, dash.no_update), 
            dash.no_update, 
            dash.no_update, dash.no_update, dash.no_update, dash.no_update,
            dash.no_update
        )

def register_magic_link_modal_callbacks(app: dash.Dash) -> None:
    r'''Register all callbacks associated with widgets in the magic link modal.'''

    @app.callback(
        dash.Output('magic-link-modal', 'opened', allow_duplicate=True),
        dash.Input('magic-link-copy-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def magic_link_button(_): return False

def register_login_modal_callbacks(app: dash.Dash) -> None:
    r'''
    Register all callbacks associated with widgets in the login modal.

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
        dash.Output('notification-container', 'sendNotifications'),

        dash.Output({'type' : 'login-button', 'index' : dash.ALL}, 'children'),
        dash.Output({'type' : 'login-button-tooltip', 'index' : dash.ALL}, 'label'),

        dash.Output('hike_names_list', 'data', allow_duplicate=True),
        dash.Output('hikelist-div', 'children', allow_duplicate=True),
        dash.Output('number_hikes', 'data', allow_duplicate=True),
        dash.Output('hikes_info', 'data', allow_duplicate=True),

        dash.Output('map-polylines', 'children', allow_duplicate=True),
        dash.Output('elevation-plot', 'style', allow_duplicate=True),
        
        dash.Input('send-login-button', 'n_clicks'),
        dash.Input('login-modal-id-input', 'n_submit'),
        dash.Input('login-modal-password-input', 'n_submit'),

        dash.State('login-modal-id-input', 'value'),
        dash.State('login-modal-password-input', 'value'),
        dash.State('login-success-notification', 'data'),
        dash.State('login-username-fail-notification', 'data'),
        dash.State('login-password-fail-notification', 'data'),
        dash.State('language', 'data'),

        prevent_initial_call=True
    )
    def secure_login(
        _1, _2, _3,
        username                   : str, 
        password                   : str,
        success_notification       : dict,
        username_fail_notification : dict,
        password_fail_notification : dict,
        language                   : LANGUAGE
        ) -> tuple[
            bool, 
            list[dict] | dash.NoUpdate, 

            tuple[str, str] | tuple[dash.NoUpdate, dash.NoUpdate],
            tuple[str, str] | tuple[dash.NoUpdate, dash.NoUpdate],
            
            list[str] | dash.NoUpdate,
            list      | dash.NoUpdate,
            int       | dash.NoUpdate,
            dict      | dash.NoUpdate,

            list[dl.Polyline] | dash.NoUpdate,
            dict[str, str]    | dash.NoUpdate
        ]:

        # If one of the fields is empty, we let the page as is
        if password is None or username is None or password == '' or username == '':
            return (
                True, dash.no_update, 
                (dash.no_update, dash.no_update), (dash.no_update, dash.no_update), 
                dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                dash.no_update, dash.no_update
            )

        res = validate_credentials(username, password)

        # res is None means the username does not exist
        if res is None:
            return (
                True, [username_fail_notification], 
                (dash.no_update, dash.no_update), (dash.no_update, dash.no_update), 
                dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                dash.no_update, dash.no_update
            )
        
        # res is False means the password is wrong
        if not res:
            return (
                True, [password_fail_notification], 
                (dash.no_update, dash.no_update), (dash.no_update, dash.no_update), 
                dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                dash.no_update, dash.no_update
            )
        
        # Password and username are both correct, we store the user ID for later queries to the db
        session['user_id'] = Users_table.get_user_id_from_username(username)

        # Load the hike list ui elements based on the data from the db
        hike_list_ui_elements = generate_hike_ui_elements_after_login(app, language)

        login_button_tooltip = app.language_handler[language]['login_logout_buttons']['logout' if 'user_id' in session else 'login']['tooltip']

        # Otherwise, sends a login success notification
        return (
            False, [success_notification], 
            (username, username), (login_button_tooltip, login_button_tooltip),
            *hike_list_ui_elements, {'display' : 'flex'}
        )
    
    @app.callback(
        dash.Output('login-modal-id-input', 'value', allow_duplicate=True),
        dash.Output('login-modal-password-input', 'value', allow_duplicate=True),
        dash.Input('login-modal', 'opened'),
        prevent_initial_call=True
    )
    def exit_login_modal(is_open: bool) -> tuple[str, str]: 
        
        if not is_open: return '', ''
        else: raise dash.exceptions.PreventUpdate

    return

def update_ui_after_single_hike_load(
        pos_absolute     : int,
        hike_name        : str,
        properties       : dict | None,
        language_dict    : dict,
        magic_link_state : bool = False
    ) -> tuple[dmc.Space, dl.Polyline, dict[str, float | int]] | None:
    r'''
    Generate the new UI components that must be updated after a new hike has been loaded.

    :param pos_absolute: absolute index of the hike in the hike list
    :param hike_name: name of the hike
    :param properties: properties of the hike store in the Store
    :param language_dict: dictionary for the hikelist element
    :param magic_link_state: True triggers a special UI for magic links, False triggers the normal UI

    :returns:
        - hikelist element widget
        - PolyLine that represents the path of the hike
        - dictionary with hike information
    '''

    # None means the parsing failed
    if properties is None: return

    color    = COLOR_PALETTE[pos_absolute]

    # Create a hike widget in the hike list
    widget   = hikelist_element_layout(
        hike_name,
        color,
        pos_absolute,
        False if pos_absolute > 0 else True,
        language_dict,
        magic_link_state = magic_link_state
    )

    max_distance = properties['distances'][-1]
    diff_height  = np.array(properties['elevations'][1:]) - np.array(properties['elevations'][:-1])
    
    positive_cumulative = diff_height[diff_height > 0].sum()
    negative_cumulative = diff_height[diff_height < 0].sum()
    
    # Add hike information to the Store component
    hike_info = {
        'lat'        : properties['center'][0],
        'lon'        : properties['center'][1],
        'zoom'       : properties['zoom'],
        'distances'  : [f'{d:.1f}' for d in properties['distances']],
        'elevations' : properties['elevations']
    }

    line = dl.Polyline(
        id        = {'type' : 'map-trace', 'index' : hike_name},
        positions = [(la, lo) for lo, la in zip(properties['lon'], properties['lat'])],
        pathOptions = {
            'color' : color
        },
        children    = dl.Popup([
            dash.html.Div(f'Distance: {max_distance:.1f} km'),
            dash.html.Div(f'Positive elevation: {positive_cumulative:.0f} m'),
            dash.html.Div(f'Negative elevation: {negative_cumulative:.0f} m')
        ])
    )

    return widget, line, hike_info

def update_ui_after_multiple_hike_loads(
    app              : dash.Dash,
    property_dict    : dict[str, dict | None],
    hike_widgets     : list,
    language         : LANGUAGE,
    hikes_info       : dict,
    magic_link_state : bool = False
) -> tuple[list, int, dict, list[dl.Polyline]]:
    r'''
    Generate the new UI components that must be updated after many new hike have been loaded.

    :param app: dash app
    :param property_dict: dictionary containing hike names as keys and dictionaries with hike properties as values
    :param hike_widgets: current widgets holding hikes in the hike list
    :param language_dict: dictionary for the hikelist element
    :param hikes_info: dictionary in Store with hike information such as center and zoom level
    :param magic_link_state: True triggers a special UI for magic links, False triggers the normal UI

    :returns:
        - list of hike element widgets
        - number of hikes
        - dictionary with hike names as keys and dictionaries with hike information as values
        - map figure
    '''

    language_dict = app.language_handler[language]['hike_panel']
    pos_init      = len(hike_widgets)

    new_hike_widgets = []
    new_traces       = []

    for pos, (hike_name, properties) in enumerate(property_dict.items()):

        out = update_ui_after_single_hike_load(
            pos_init + pos,
            hike_name,
            properties,
            language_dict,
            magic_link_state=magic_link_state
        )

        if out is None: continue

        new_hike_widgets.append(out[0])
        new_traces.append(out[1])

        # Add hike information to the Store component
        hikes_info[hike_name] = out[2]

    hike_widgets.extend(new_hike_widgets)

    return hike_widgets, len(hike_widgets), hikes_info, new_traces

def generate_hike_ui_elements_after_login(
        app: dash.Dash, language: LANGUAGE, magic_link_state: bool = False
    ) -> tuple[list[str], list, int, dict, list[dl.Polyline]]:
    r'''
    Generate all the ui elements that need to be updated after login.

    :param app: dash app
    :param language: selected language
    :param magic_link_state: True triggers a special UI for magic links, False triggers the normal UI

    :returns:
        - list of hike names in the same order as they appear in the hike list widget
        - list of hike element widgets
        - number of hikes
        - dictionary with hike names as keys and dictionaries with hike information as values
        - list of Polyline object to draw on the map (hike paths)
    '''

    # Query hikes database associated to the user
    hike_properties = execute_get_query(f'''
        SELECT name, latitude, longitude, center_lat, center_lon, zoom, distances, elevations
        FROM hikes
        WHERE user_id = '{session["user_id"]}';
    ''')

    # Build the dictionary with hike properties
    property_dict = {}
    hike_names    = []

    for hike in hike_properties:

        hike_names.append(hike[0])

        property_dict[hike[0]]               = {}
        property_dict[hike[0]]['lat']        = hike[1]
        property_dict[hike[0]]['lon']        = hike[2]
        property_dict[hike[0]]['center']     = (hike[3], hike[4])
        property_dict[hike[0]]['zoom']       = hike[5]
        property_dict[hike[0]]['distances']  = hike[6]
        property_dict[hike[0]]['elevations'] = hike[7]

    ui_elements = update_ui_after_multiple_hike_loads(
        app, property_dict, [],
        language, {},
        magic_link_state = magic_link_state
    )

    # Create a new figure and update all ui elements related to hikes
    return hike_names, *ui_elements