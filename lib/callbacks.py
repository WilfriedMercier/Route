import dash
import typing
import dash_mantine_components as     dmc
import plotly.graph_objects    as     go
import dash_leaflet            as     dl
import numpy                   as     np
from   urllib.parse            import urlparse, parse_qs
from   flask                   import session
from   plotly.colors           import qualitative
from   textwrap                import dedent

from   .errors                 import (
    UnsupportedFileFormatError,
    NoHikeForMagicLink,
    NoHikeIDInDB,
    NoMagicLinkForHikeID,
    NoUsernameInDB,
    NoUserIdInDB,
    WrongPassword,
    WrongUsername
)
from   .types                  import (
    HikeDataForMarker, 
    HikeProps, 
    HikeInfo,
    HikeDataForElevationPlot,
    Notification,
    Dummy,
    DummyWithTraces,
    EMPTY_HIKE_DATA_FOR_PLOT
)

from   .lang                   import LANGUAGE
from   .io                     import decode_and_process_uploaded_file
from   .components             import hikelist_element_layout, language_element, HandleShortcut
from   .components.notifications import (
    login_success_notification,
    logout_success_notification,
    wrong_magic_link_notification,
    hike_upload_success_notification,
    hike_upload_format_fail_notification,
    hike_upload_already_there_fail_notification,
)

from   .components.map         import generate_new_figure, generate_leaflet_map_figure
from   .misc                   import check_if_hike_is_loaded
from   .database               import (
    Hikes_table,
    Users_table,
    Magic_links_table,
    validate_credentials, 
    execute_get_query,
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
    register_colorpicker_modal_callbacks(app)
    register_clientside_callbacks(app)
    register_validate_modal_callbacks(app)

    return

def register_clientside_callbacks(app: dash.Dash) -> None:
    r'''
    Register all clientside callbacks.

    :param app: dash application
    '''

    # Callback used when the user is hovering over the elevation plot.
    # This prevents constantly asking the server to update the marker on the map.
    app.clientside_callback(
        dash.ClientsideFunction(
            namespace     = 'clientside',
            function_name = 'elevation_plot_hover_callback'
        ),
        dash.Output('dummy', 'data', allow_duplicate=True),
        dash.Input('elevation-plot', 'hoverData'),
        dash.State('map', 'bounds'),
        dash.State('selected-hike-data-for-marker', 'data'),
        dash.State('selected-hike-props', 'data'),
        dash.State('dummy', 'data'),
        prevent_initial_call=True
    )

    # Callback used to update the elevation plot and the map when the slider is used in mobile mode.
    # This is much faster than going back and forth to the server.
    app.clientside_callback(
        dash.ClientsideFunction(
            namespace     = 'clientside',
            function_name = 'slider_callback'
        ),
        dash.Output('dummy', 'data'),
        dash.Input('elevation-plot-slider', 'value'),
        dash.State('selected-hike-data-for-plot', 'data'),
        dash.State('selected-hike-data-for-marker', 'data'),
        dash.State('map', 'bounds'),
        dash.State('selected-hike-props', 'data'),
        dash.State('dummy', 'data'),
    )

    app.clientside_callback(
        dash.ClientsideFunction(
            namespace     = 'clientside',
            function_name = 'hide_marker_and_highlight_line'
        ),
        dash.Output('dummy', 'data', allow_duplicate=True),
        dash.Input('map', 'zoom'),
        dash.State('dummy', 'data'),
        prevent_initial_call=True
    )

    return

def register_keydown_callbacks(app: dash.Dash) -> None:
    r'''
    Register callabacks associated to different key shortcuts being pressed.

    :param app: dash application
    '''
    
    @app.callback(
        dash.Output('hike-panel',  'opened', allow_duplicate=True),
        dash.Output('login-modal', 'opened', allow_duplicate=True),

        dash.Input('keyboard',   'n_keydowns'),
        dash.State('keyboard',   'keydown'),
        dash.State('hike-panel', 'opened'), 
        prevent_initial_call=True
    )
    def register_keydown(_, keydown: dict, is_hike_panel_open: bool) -> tuple[bool | dash.NoUpdate, bool | dash.NoUpdate]:
        r'''
        Callaback called whenever a registered key is pressed. Used to handle shortcuts.

        :param keydown: dictionary with 'key' holding the pressed key and 'altKey' indicating whether alt is pressed as well
        :param is_hike_panel_open: whether the hike panel is open or not

        :returns: 
            - if Alt + L, see :py:`HandleShortcut.alt_l_key_combination`
            - if Alt + A, see :py:`HandleShortcut.alt_a_key_combination`
        '''

        # Shortcut to open/close the hike panel (not working with a magic link)
        if keydown['key'] == 'l' and keydown['altKey']:
            return HandleShortcut.alt_l_key_combination(is_hike_panel_open)
        
        # Shortcut to switch between light and dark modes
        elif not session['magic-link'] and keydown['key'] == 'a' and keydown['altKey']:
            return HandleShortcut.alt_a_key_combination()
        
        raise dash.exceptions.PreventUpdate
    
    return

def register_burger_callbacks(app: dash.Dash) -> None:
    r'''
    Register all callbacks that define the behaviour of the burger component in the topbar.

    :param app: dash application
    '''

    @app.callback(
        dash.Output("appshell", "navbar"),

        dash.Input( "burger",   "opened"),
        dash.State( "appshell", "navbar"),
    )
    def toggle_navbar(opened: bool, navbar: dict[str, typing.Any]):
        r'''
        Callback called whenever the burger UI element is clicked.

        :param opened: whether the burger has state opened or not
        :param navbar: dictionary with key-value pairs that describe the navbar (i.e., the menubar)

        :returns: the new navbar with a collapsed state or not
        '''

        navbar["collapsed"] = {"mobile": not opened, 'desktop' : not opened}
        return navbar

    return

def register_ui_init_callbacks(app: dash.Dash) -> None:
    r'''
    Register all callbacks that initialize the UI based on the input token.

    :param app: dash application
    '''

    @app.callback(
        dash.Output('map-div', 'style', allow_duplicate=True),
        dash.Output('base-url', 'data'),
        dash.Output('magic-link', 'data'),

        dash.Input('url', 'href'),

        prevent_initial_call = True
    )
    def render_ui(url: str) -> tuple[
            dict[str, typing.Any] | dash.NoUpdate, # map -> style
            str,  # base-url -> data
            str,  # magic-link -> data
        ]:
        r'''
        Callback used at startup to define how the UI is rendered.

        .. note::
            This is the first pass of the UI rendering. It basically sets the height of the map and defines the magic-link value
            which is used to trigger the second pass that updates all other UI elements.

        :param url: url of the page
        :param language: selected language
        :param notification: notification shown when the magic link is wrong
        :param theme: theme from the two theme buttons
        '''

        parsed_url   = urlparse(url)
        base_url     = parsed_url.scheme + '://' + parsed_url.netloc
        query_params = parse_qs(parsed_url.query)
        token_list   = query_params.get('token')

        # Case without a magic link
        if (token_list is None or len(token_list) != 1):
            return dash.no_update, base_url, ''
        
        # Case with a magic link
        return {'height' : '70%'}, base_url, token_list[0]
    
    @app.callback(
        dash.Output('map-div', 'children', allow_duplicate=True),
        dash.Output({'type' : 'login-button', 'index' : dash.ALL}, 'style', allow_duplicate=True),
        dash.Output({'type' : 'login-button', 'index' : dash.ALL}, 'children', allow_duplicate=True),
        dash.Output({'type' : 'login-button-tooltip', 'index' : dash.ALL}, 'label', allow_duplicate=True),
        dash.Output('hikelist-div',           'children',          allow_duplicate=True),
        dash.Output('number-hikes',           'data',              allow_duplicate=True),
        dash.Output('hikes-info',             'data',              allow_duplicate=True),
        dash.Output('map-polylines',          'children',          allow_duplicate=True),
        dash.Output('elevation-plot-stack',   'style',             allow_duplicate=True),
        dash.Output('upload-hike-button',     'style',             allow_duplicate=True),
        dash.Output('notification-container', 'sendNotifications', allow_duplicate=True),

        dash.Input('magic-link', 'data'),
        dash.State('language', 'data'),

        prevent_initial_call = True
    )
    def render_ui_second_pass(
            magic_link :  str | None,
            language   : LANGUAGE,
        ) -> tuple[
            dl.Map, # map -> children
            tuple[dict[str, str], dict[str, str]] | tuple[dash.NoUpdate, dash.NoUpdate], # all login-button -> style
            tuple[str, str]      | tuple[dash.NoUpdate, dash.NoUpdate], # all login-button -> children
            tuple[str, str]      | tuple[dash.NoUpdate, dash.NoUpdate], # all login-button-tooltip -> label
            list[dmc.Space]      | dash.NoUpdate, # hikelist-div -> children
            int                  | dash.NoUpdate, # number-hikes -> data
            dict[str, HikeInfo]  | dash.NoUpdate, # hikes-info -> data
            list[dl.Polyline]    | dash.NoUpdate, # map-polylines -> children
            dict[str, str]       | dash.NoUpdate, # elevation-plot-plot -> style
            dict[str, str]       | dash.NoUpdate, # upload-hike-button -> style
            list[Notification]   | dash.NoUpdate, # notification-container -> sendNotifications
        ]:
        r'''
        Second pass of the UI rendering used to allow the leaflet map to resize before triggering other events.

        :param magic_link: magic link provided in the URL or ''
        :param language: current language of the application
        '''

        if magic_link is None: raise dash.exceptions.PreventUpdate

        # Case with a magic link. Note the following are disabled when opening with a magic link:
        # - all login/logout buttons
        # - upload hike button
        # - all share hike buttons
        if magic_link != '':

            try:
                widgets, n_hikes, hikes_info, traces = handle_with_magic_link(magic_link, language)
            except NoHikeForMagicLink: # Case when magic link incorrect

                notification = wrong_magic_link_notification(
                    app.language_handler[language]['notifications']
                )

                return (
                    generate_leaflet_map_figure(),
                    (dash.no_update, dash.no_update),
                    (dash.no_update, dash.no_update),
                    (dash.no_update, dash.no_update),
                    dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                    dash.no_update,  dash.no_update, [notification]
                )

            # Case when magic link is correct
            return (
                generate_leaflet_map_figure(),
                ({'display' : 'none'}, {'display' : 'none'}),
                (dash.no_update, dash.no_update),
                (dash.no_update, dash.no_update),
                widgets, n_hikes, hikes_info, traces,
                {'display' : 'flex'},  {'display' : 'none'}, dash.no_update
            )
        
        # Case without a magic link
        else:

            (
                button_style_1, button_style_2,
                widgets, n_hikes, hikes_info, traces,
                login_button, login_tooltip
            ) = handle_without_magic_link(language)

            return (
                generate_leaflet_map_figure(),
                (button_style_1, button_style_2), 
                (login_button, login_button),
                (login_tooltip, login_tooltip),
                widgets, n_hikes, hikes_info, traces,
                {'display' : 'flex' if 'user_id' in session else 'none'}, 
                dash.no_update, dash.no_update
            )
        
    def handle_with_magic_link(
            magic_link : str, 
            language   : LANGUAGE
        ) -> tuple[list[dmc.Space], int, dict[str, HikeInfo], list[dl.Polyline]]:
        r'''
        Handle the rendering of the UI elements when the user is connecting with a magic link.

        :param magic_link: magic link provided in the url
        :param language: selected language

        :returns:
            - list of hike element widgets
            - number of hikes
            - dictionary with hike names as keys and dictionaries with hike information as values
            - list of Polylines object to draw on the map (hike paths)

        :raises: NoHikeForMagicLink if the magic link is wrong
        '''

        # Store in session manager that a magic link is used
        session['magic-link'] = True

        # Get the hike ID associated to the magic link. If None, no link 
        hike_id = Magic_links_table.get_hike_id_from_magic_link(magic_link)
        
        hikes_info, widgets, traces = generate_hike_ui_elements_with_hike_id(app, language, hike_id)

        # Create a new figure and update all ui elements related to hikes
        return widgets, len(widgets), hikes_info, traces

    def handle_without_magic_link(
            language: LANGUAGE
        ) -> tuple[
            dict[str, str], 
            dict[str, str], 
            list[dmc.Space], 
            int, 
            dict[str, HikeInfo], 
            list[dl.Polyline],
            str,
            str
        ]:
        r'''
        Handle the rendering of the UI elements when the user is not connecting with a magic link.

        :param language: selected language

        :returns:
            - a dictionary containing the style for the first login button
            - a dictionary containing the style for the second login button
            - list of hike widgets
            - number of loaded hikes
            - dictionary with information for each hike
            - list of Polylines object to draw on the map (hike paths)
            - text shown in the login buttons
            - text shown in the tooltips of the login buttons
        '''

        # Store in session manager that a magic link is not used
        session['magic-link'] = False

        # User session still active in the cookies
        if 'user_id' in session:

            # All ui elements associated to the hikes
            hikes_info, widgets, traces = generate_hike_ui_elements_with_login(app, language)

            login_button  = Users_table.get_username_from_user_id(session['user_id'])
            login_tooltip = app.language_handler[language]['login_logout_buttons']['logout']['tooltip']

            return (
                {'display' : 'flex'}, {'display' : 'flex'},
                widgets, len(widgets), hikes_info, traces,
                login_button, login_tooltip
            )
        
        login_button  = app.language_handler[language]['login_logout_buttons']['login']['text']
        login_tooltip = app.language_handler[language]['login_logout_buttons']['login']['tooltip']

        # User session not active in the cookies
        return (
            {'display' : 'flex'}, {'display' : 'flex'},
            [], 0, {}, [],
            login_button, login_tooltip
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

        dash.Output({'type' : 'hikelist-delete-button-tooltip', 'index' : dash.ALL}, 'label'),
        dash.Output({'type' : 'hikelist-hide-button-tooltip',   'index' : dash.ALL}, 'label'),
        dash.Output({'type' : 'hikelist-colorpicker-tooltip',   'index' : dash.ALL}, 'label'),
        dash.Output({'type' : 'hikelist-share-button-tooltip',  'index' : dash.ALL}, 'label'),
        dash.Output('upload-hike-button', 'children'),

        dash.Output({'type' : 'login-button', 'index' : dash.ALL}, 'children', allow_duplicate=True),
        dash.Output({'type' : 'login-button-tooltip', 'index' : dash.ALL}, 'label', allow_duplicate=True),

        dash.Output('login-modal', 'title'),
        dash.Output('login-modal-id-input', 'label'),
        dash.Output('login-modal-id-input', 'placeholder'),
        dash.Output('login-modal-password-input', 'label'),
        dash.Output('login-modal-password-input', 'placeholder'),
        dash.Output('send-login-button', 'children'),

        dash.Output({'type' : 'language-dropdown', 'index' : dash.ALL}, 'children', allow_duplicate=True),
        dash.Output('magic-link-modal-text', 'children'),
        dash.Output('magic-link-modal', 'title'),

        dash.Output('elevation-plot', 'figure', allow_duplicate=True),
  
        dash.Input({'type': 'language-button', 'index': dash.ALL}, 'n_clicks'),
        dash.State('number-hikes', 'data'),
        dash.State('elevation-plot', 'figure'),

        prevent_initial_call=True,
    )
    def language_selection(n_clicks, n_hikes: int, ev_plot) -> tuple[
        str, 
        str, str, str, str, str, str,
        list[str], list[str], list[str], list[str], tuple[str],
        tuple[str, dash.NoUpdate] | tuple[dash.NoUpdate, dash.NoUpdate], tuple[str, str],
        str, str, str, str, str, str,
        tuple[list, list],
        str, str,
        go.Figure
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

        # Update the elevation plot with the right translation
        fig = go.Figure(ev_plot)
        fig.update_layout(
            xaxis_title = translation['elevation_plot']['xlabel'],
            yaxis_title = translation['elevation_plot']['ylabel']
        )

        fig.update_traces(
            hovertemplate=dedent(f'''\
                <extra></extra>
                <b>{translation['elevation_plot']['hovertemplate']['distance']}:</b> %{{x:.1f}} km<br>
                <b>{translation['elevation_plot']['hovertemplate']['remaining_distance']}:</b> %{{customdata[0]:.1f}} km<br>
                <b>{translation['elevation_plot']['hovertemplate']['elevation']}:</b> %{{y:.0f}} m<br>
                <b>{translation['elevation_plot']['hovertemplate']['slope']}:</b> %{{customdata[1]:.1f}}%
            ''')
        )

        return (
            lang,
            translation['topbar']['theme_switcher']['tooltip'],
            translation['menubar']['hike_panel_button']['text'],
            translation['menubar']['hike_panel_button']['tooltip'],
            translation['menubar']['hall_of_fame_button']['text'],
            translation['menubar']['hall_of_fame_button']['tooltip'],
            translation['hike_panel']['title'],

            [translation['hike_panel']['delete_button']['tooltip']] * n_hikes,
            [translation['hike_panel']['hide_button'][  'tooltip']] * n_hikes,
            [translation['hike_panel']['colorpicker'][  'tooltip']] * n_hikes,
            [translation['hike_panel']['share_button'][ 'tooltip']] * n_hikes,
            (translation['hike_panel']['upload_button']['text'],),

            (login_button_text, login_button_text),
            (login_button_tooltip, login_button_tooltip),

            translation['login_modal']['title'],
            translation['login_modal']['user_id_input']['label'],
            translation['login_modal']['user_id_input']['placeholder'],
            translation['login_modal']['user_password_input']['label'],
            translation['login_modal']['user_password_input']['placeholder'],
            translation['login_modal']['send_login_button']['text'],

            (language_dropdown, language_dropdown),

            translation['magic_link_modal']['text'],
            translation['magic_link_modal']['title'],

            fig
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
    def hike_panel_button(_) -> typing.Literal[True]:
        r'''Callback used when the hike panel button is clicked.'''

        return True
    
    return

def register_hike_drawer_callbacks(app: dash.Dash) -> None:
    r'''
    Register all callbacks associated to widgets in the hike drawer.

    :param app: dash application
    '''

    @app.callback(
        dash.Output('selected-hike-props',           'data'),
        dash.Output('selected-hike-data-for-marker', 'data'),
        dash.Output('selected-hike-data-for-plot',   'data'),

        dash.Output({'type' : 'hikelist-button', 'index' : dash.ALL}, 'style'),

        dash.Output('map', 'viewport'),

        dash.Output("burger", "opened"),
        dash.Output('hike-panel', 'opened', allow_duplicate=True),

        dash.Output('elevation-plot', 'figure'),

        dash.Output('elevation-plot-slider', 'max'),

        dash.Input( {'type' : 'hikelist-button', 'index' : dash.ALL}, 'n_clicks'),
        dash.State('hikes-info', 'data'),
        dash.State({'type' : 'hikelist-colorpicker', 'index' : dash.ALL}, 'color'),
        dash.State('language', 'data'),

        prevent_initial_call = True
    )
    def hike_button(
        _,
        hikes_info : dict[str, HikeInfo], 
        colors     : list[str],
        language   : LANGUAGE
    ) -> tuple[
            HikeProps, HikeDataForMarker, HikeDataForElevationPlot,
            list[dict[str, str]], 
            dict,
            typing.Literal[False], 
            typing.Literal[False],
            go.Figure,
            int
        ]:
        r'''
        Callback used when a hike is selected in the hike list.

        :param hikes_info: hike properties containing information such as center and zoom level
        :param colors: list of colors associated to each colorpicker
        :param language: current language of the UI

        :returns:
            - dictionary with properties corresponding to the selected hike
            - dictionary with data for the map corresponding to the selected hike
            - dictionary with data for the elevation plot corresponding to the selected hike
            - list of dictionaries with styles for the hikelist buttons
            - dictionary with properties to modify the viewport of the map (i.e. center and zoom)
            - False to close the navbar associated to the burger object
            - False to close the hike-panel
            - a new figure for the elevation plot with updated data and properties
            - the maximum value of the slider in mobile mode
        '''

        if _ is None: raise dash.exceptions.PreventUpdate

        ctx = dash.callback_context

        if ctx is None or not ctx.triggered: raise dash.exceptions.PreventUpdate

        # Extract the ID of the clicked button
        hike_name = ctx.triggered_id['index'] # type: ignore

        styles = []
        for pos, name in enumerate(hikes_info.keys()):
            
            styles.append(
                {} if hike_name != name else 
                {'backgroundColor': 'var(--custom-theme-color)', 'color' : 'white'}
            )
            
            if hike_name == name: color = colors[pos]

        # Get distances and elevations for the given hike
        info  = hikes_info[hike_name]

        # Store info about the selected hike
        selected_hike_props = HikeProps(
            name  = hike_name,
            color = color
        )

        selected_hike_lat_lon = HikeDataForMarker(
            latitudes  = info['latitudes'],
            longitudes = info['longitudes']
        )

        selected_hike_dist_elev = HikeDataForElevationPlot(
            distances  = info['distances'],
            elevations = info['elevations']
        )

        fig = generate_new_figure(
            np.array(info['distances']), 
            np.array(info['elevations']), 
            color,
            app.language_handler[language]['elevation_plot']
        )

        return (
            selected_hike_props, selected_hike_lat_lon, selected_hike_dist_elev,
            styles,
            {
                #'center'     : (info['center_lat'], info['center_lon']),
                'bounds'     : (
                    (min(info['latitudes']), min(info['longitudes'])), 
                    (max(info['latitudes']), max(info['longitudes']))
                ),
                'transition' : "flyTo"
            },
            False, False,
            fig, len(info['distances'])
        )
    
    @app.callback(
        dash.Output('colorpicker-modal', 'opened', allow_duplicate=True),
        dash.Output('colorpicker', 'value', allow_duplicate=True),
        dash.Output('colorpicker-selected-id', 'data'),

        dash.Input({'type' : 'hikelist-colorpicker', 'index' : dash.MATCH}, 'n_clicks'),
        dash.State({'type' : 'hikelist-colorpicker', 'index' : dash.MATCH}, 'color'),
        prevent_initial_call=True
    )
    def colorpicker_click(
            _     : int | None, 
            color : str
        ) -> tuple[typing.Literal[True], str, str]:
        r'''
        Callback called whenever the given colorpicker is clicked in the hike list panel.

        :param colors: colors selected by the colorpickers

        :returns:
            - True to open the colorpicker modal
            - the color of the clicked button to pass it as default value to the colorpicker
            - ID of the clicked colorpicker button
        '''

        if _ is None: raise dash.exceptions.PreventUpdate

        ctx = dash.callback_context

        if ctx is None or not ctx.triggered: raise dash.exceptions.PreventUpdate

        triggered_id = ctx.triggered_id['index'] # type: ignore
        
        return True, color, triggered_id

    @app.callback(
        dash.Output({'type' : 'hikelist-button',               'index' : dash.MATCH}, 'disabled'),
        dash.Output({'type' : 'hikelist-colorpicker',          'index' : dash.MATCH}, 'disabled'),
        dash.Output({'type' : 'hikelist-share-button',         'index' : dash.MATCH}, 'disabled'),
        dash.Output({'type' : 'hikelist-colorpicker-tooltip',  'index' : dash.MATCH}, 'disabled'),
        dash.Output({'type' : 'hikelist-share-button-tooltip', 'index' : dash.MATCH}, 'disabled'),
        dash.Output({'type' : 'map-trace',                     'index' : dash.MATCH}, 'pathOptions', allow_duplicate=True),

        dash.Input({'type' : 'hikelist-hide-button', 'index' : dash.MATCH}, 'checked'),
        dash.State({'type' : 'hikelist-colorpicker', 'index' : dash.MATCH}, 'color'),

        prevent_initial_call = True
    )
    def hide_button(
        checked : bool,
        color   : str,
    ) -> tuple[bool, bool, bool, bool, bool, dict]:
        r'''
        Callback used when the hide button is toggled.

        :param checked: whether the hide button is checked
        :param color: current color for the colorpicker button

        :returns: a tuple containing
            - 5 times the same True or False value for each hike wiget UI element (True to disable, False to enable)
            - a dictionary inside specifying the color of the line on the map (transparent if hidden)
        '''

        output     = not checked

        # Change disabled hikes color to transparent
        hike_color = {'color' : color if checked else 'rgba(0, 0, 0, 0)'}

        return output, output, output, output, output, hike_color
    
    @app.callback(
        dash.Output('magic-link-modal', 'opened'),
        dash.Output('magic-link-copy-button', 'value'),
        dash.Output('magic-link-copy-button', 'children'),

        dash.Input({'type' : 'hikelist-share-button', 'index' : dash.MATCH}, 'n_clicks'),
        dash.State('base-url', 'data'),
        prevent_initial_call = True
    )
    def share_hike(
            _ : int | None,
            base_url : str
        ) -> tuple[typing.Literal[True], str, str]:
        r'''
        Callback used when any of the share buttons is clicked.
        
        :param n_clicks: number of clicks in each share button
        :param base_url: base url at which the application is accessible 

        :returns: a tuple with
            - True,
            - magic link
            - magic link
        '''

        if _ is None: raise dash.exceptions.PreventUpdate

        ctx = dash.callback_context

        if ctx is None or not ctx.triggered: raise dash.exceptions.PreventUpdate

        triggered_id: dict = ctx.triggered_id # type: ignore
        
        try:
            hike_id      = Hikes_table.get_hike_id_from_user_id_and_hike_name(
                session['user_id'], triggered_id['index']
            )
        except NoHikeIDInDB: raise dash.exceptions.PreventUpdate
        
        try:
            magic_link_id = Magic_links_table.get_magic_link_from_hike_id(hike_id)
        except NoMagicLinkForHikeID:

            Magic_links_table.insert_magic_link_into_db(hike_id)

            # Retrieve the magic link
            magic_link_id = Magic_links_table.get_magic_link_from_hike_id(hike_id)

        magic_link = f'{base_url}?token={magic_link_id}'

        return True, magic_link, magic_link
    
    @app.callback(
        dash.Output('validate-modal', 'opened'),
        dash.Output('validate-modal', 'title'),
        dash.Output('validate-modal-yes',  'children'),
        dash.Output('validate-modal-no',   'children'),
        dash.Output('validate-modal-text', 'children'),

        dash.Input({'type' : 'hikelist-delete-button', 'index' : dash.MATCH}, 'n_clicks'),
        dash.State('language', 'data')
    )
    def delete_hike(_: int | None, language: LANGUAGE) -> tuple[typing.Literal[True], str, str, str, str]:
        r'''
        Callback called when one of the delete hike buttons is clicked in the hike drawer.

        :param language: current language of the application

        :returns: a tuple with
            - True,
            - name of the hike
            - text shown in the yes button
            - text shown in the no button
            - text shown in the confirm modal
        '''
        
        if _ is None: raise dash.exceptions.PreventUpdate

        ctx = dash.callback_context

        if ctx is None or not ctx.triggered: raise dash.exceptions.PreventUpdate

        triggered_id: dict = ctx.triggered_id # type: ignore

        try:
            session['hike-to-delete'] = triggered_id['index']
        except NoHikeIDInDB: raise dash.exceptions.PreventUpdate

        translation = app.language_handler[language]['validate_modal']

        return (
            True, 
            triggered_id['index'], 
            translation['yes_button']['text'],
            translation['no_button']['text'],
            translation['text'],
        )
    
    return

def register_upload_hike_callbacks(app: dash.Dash) -> None:
    r'''All callbacks associated to uploading hikes.'''

    @app.callback(
        dash.Output('map-div', 'children', allow_duplicate=True),
        dash.Output('map-polylines', 'children', allow_duplicate=True),
        dash.Input('dummy-with-traces', 'data'),
        prevent_initial_call=True
    )
    def upload_hike_second_pass(dummy: DummyWithTraces) -> tuple[dl.Map, list[dl.Polyline]]:

        if dummy is None: raise dash.exceptions.PreventUpdate

        return generate_leaflet_map_figure(), dummy['traces']
    
    @app.callback(
        dash.Output('hikelist-div', 'children'),
        dash.Output('number-hikes', 'data'),
        dash.Output('hikes-info', 'data'),

        dash.Output('notification-container', 'sendNotifications', allow_duplicate=True),
        dash.Output('elevation-plot-stack', 'style', allow_duplicate=True),
        dash.Output('map-div', 'style', allow_duplicate=True),

        dash.Output('dummy-with-traces', 'data', allow_duplicate=True),
        
        dash.Input('upload-hike-button', 'contents'),
        dash.State('upload-hike-button', 'filename'),
        dash.State('hikelist-div', 'children'),
        dash.State('map-polylines', 'children'),
        dash.State('language', 'data'),
        dash.State('hikes-info', 'data'),
        dash.State('dummy-with-traces', 'data'),
        prevent_initial_call = True
    )
    def upload_hike_first_pass(
        file_contents : list[str] | None, 
        filenames     : list[str], 
        hike_widgets  : list[dmc.Space],
        traces        : list[dl.Polyline],
        language      : LANGUAGE,
        hikes_info    : dict[str, HikeInfo],
        dummy         : DummyWithTraces
    ) -> tuple[
            list[dmc.Space]     | dash.NoUpdate, 
            int                 | dash.NoUpdate, 
            dict[str, HikeInfo] | dash.NoUpdate,
            list[Notification],
            dict[str, str]      | dash.NoUpdate,
            dict[str, str]      | dash.NoUpdate,
            DummyWithTraces     | dash.NoUpdate
        ]:
        r'''
        Actions taken when a hike is loaded through the load hike button.

        .. note:
            This is the first pass. The second pass is called when the dummy dcc.Store element changes.

        :param file_contents: list containing the content of each loaded file
        :param filenames: list of file names
        :param hike_widgets: list of hike element UI widgets already present in the UI
        :param traces: list of map traces already drawn
        :param language: current language of the application
        :param hikes_info: dictionary-like `HikeInfo` object containing all the information about all the loaded hikes
        :param dummy: dummy object that will be modified

        :returns:
            - updated list of hike widgets
            - updated number of hikes
            - updated `HikeInfo` object
            - notification to send if any
            - dictionary indicating whether the elevation plot should be visible or not
            - dictionary indicating the height of the map
            - dummy object containing the traces used to trigger the second rendering pass
        '''

        if file_contents is None or len(file_contents) == 0: raise dash.exceptions.PreventUpdate

        translation = app.language_handler[language]['notifications']

        # Default notification is success
        notification = hike_upload_success_notification(translation)
        
        # Default values if there is an error when uploading a hike
        new_widgets    : list[dmc.Space]     | dash.NoUpdate = dash.no_update
        n_hikes        : int                 | dash.NoUpdate = dash.no_update
        out_hikes_info : dict[str, HikeInfo] | dash.NoUpdate = dash.no_update
        ev_style       : dict[str, str]      | dash.NoUpdate = dash.no_update
        map_style      : dict[str, str]      | dash.NoUpdate = dash.no_update
        out_dummy      : DummyWithTraces     | dash.NoUpdate = dash.no_update

        # List of names of hikes already loaded
        hike_names   = list(hikes_info.keys())

        # Extract the properties of the loaded hikes
        hike_properties : dict[str, HikeInfo] = {}

        for content, filename in zip(file_contents, filenames):

            try: hike_name, properties = decode_and_process_uploaded_file(content, filename)

            # Wrong file format cancels loading hikes
            except UnsupportedFileFormatError:
                
                notification = hike_upload_format_fail_notification(translation)
                if 'message' in notification: notification['message'] += filename
                break

            # If the hike is already loaded, we do not load any hikes. Users must only provide files that are not loaded yet
            if check_if_hike_is_loaded(hike_name, hike_names):

                notification = hike_upload_already_there_fail_notification(translation)
                if 'message' in notification: notification['message'] += filename
                break

            hike_properties[hike_name] = properties

        else:

            # If logged in, we send hikes to the db
            if 'user_id' in session: 
                Hikes_table.insert_hikes_into_db(session['user_id'], hike_properties)

            new_widgets, new_traces = update_ui_after_multiple_hike_loads(
                app, 
                hike_properties,
                hike_widgets,
                language,
                magic_link_state = 'user_id' not in session
            )

            # Combine previous elements with new ones
            n_hikes        = len(new_widgets)
            out_traces     = traces + new_traces
            out_hikes_info = hikes_info | hike_properties
            ev_style       = {'display' : 'flex'}
            map_style      = {'height' : '70%'}

            out_dummy = DummyWithTraces(
                n_clicks = dummy['n_clicks'] + 1,
                traces   = out_traces
            )

        return (
            new_widgets, n_hikes, out_hikes_info, 
            [notification], ev_style, map_style,
            out_dummy
        )

def register_login_buttons_callbacks(app: dash.Dash) -> None:
    r'''
    Register all callbacks associated to widgets in the topbar.

    :param app: dash application
    '''

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

            list[Notification] | dash.NoUpdate
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
                [logout_success_notification(translation['notifications'])]
            )

        # Handle login button click
        return (
            not opened, 
            (dash.no_update, dash.no_update), 
            (dash.no_update, dash.no_update), 
            dash.no_update, dash.no_update, dash.no_update, 
            dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update,
            dash.no_update, dash.no_update,
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

def register_colorpicker_modal_callbacks(app: dash.Dash) -> None:
    r'''Register all callbacks associated to the modal in which resides the colorpicker.'''

    @app.callback(
        dash.Output({'type' : 'hikelist-colorpicker',  'index' : dash.ALL}, 'color'),
        dash.Output('selected-hike-props', 'data', allow_duplicate=True),

        dash.Output({'type' : 'map-trace', 'index' : dash.ALL}, 'pathOptions', allow_duplicate=True),
        dash.Output('elevation-plot', 'figure', allow_duplicate=True),

        dash.Input('colorpicker', 'value'),
        dash.State('colorpicker-selected-id', 'data'),
        dash.State({'type' : 'hikelist-colorpicker',  'index' : dash.ALL}, 'id'),
        dash.State('selected-hike-props', 'data'),
        dash.State('selected-hike-data-for-plot', 'data'),
        dash.State('language', 'data'),

        prevent_initial_call=True
    )
    def colorpicker_selection(
            selected_color  : str | None, 
            index           : str,
            colorpicker_ids : list[dict[str, str]],
            hike_props      : HikeProps,
            dist_elev       : HikeDataForElevationPlot,
            language        : LANGUAGE,
        ) -> tuple[
            list[str | dash.NoUpdate], 
            HikeProps,
            list[dict[str, str] | dash.NoUpdate], 
            go.Figure | dash.NoUpdate
        ]:
        r'''
        Callback used whenever a color is picked in the colorpicker modal.

        :param selected_color: color corresponding to the colorpicker button clicked in the hike list panel. This is used to setup the default color of the colorpicker when loading
        :param index: index identifying the hike corresponding to the button clicked
        :param colorpicker_ids: identifiers of all the colorpicker buttons in the hike list panel
        :param hike_props: properties associated to the clicked colorpicker button
        :param dist_elev: object containing distance and elevation data for the elevation plot
        :param language: current language of the UI

        :returns:
            - color (or dash.no_update) for all the colorpicker buttons. Only the clicked button is updated
            - dictionary with properties associated to the hike. The color information is updated
            - list of dictionaries with updated colors for the map
            - figure for the elevation plot with an updated color if it corresponds to the currently selected hike. Otherwise dash.no_update
        '''

        # If data is missing, we prevent any update
        if selected_color is None or index == '' or hike_props == {} or dist_elev == EMPTY_HIKE_DATA_FOR_PLOT: 
            raise dash.exceptions.PreventUpdate

        # If the user is changing the color of the selected hike, we update the color attribute in the Store
        if hike_props['name'] == index: hike_props['color'] = selected_color

        # Only update the color of the colorpicker button which is being changed
        output_colors = [
            selected_color if index == colorpicker_id['index']
            else dash.no_update
            for colorpicker_id in colorpicker_ids
        ]

        # If the index of the changed color does not match the selected hike, we do not update the elevation plot color
        if index != hike_props['name']:
            fig = dash.no_update
        else:
            fig = generate_new_figure(
                np.array(dist_elev['distances']), 
                np.array(dist_elev['elevations']), 
                selected_color,
                app.language_handler[language]['elevation_plot']
            )

        # Only update the color of the path on the map corresponding to the button being changed
        map_props = [
            {'color' : selected_color} if index == colorpicker_id['index']
            else dash.no_update
            for colorpicker_id in colorpicker_ids
        ]

        return output_colors, hike_props, map_props, fig
    
def register_validate_modal_callbacks(app: dash.Dash) -> None:
    r'''
    Register all callbacks associated with widgets in the validate modal.

    :param app: dash application
    '''

    @app.callback(
        dash.Output('validate-modal', 'opened', allow_duplicate=True),
        dash.Input('validate-modal-no', 'n_clicks'),
        prevent_initial_call=True
    )
    def no_button(_) -> bool: 
        r'''Callback used when the 'No' button is pressed.'''

        return False

    @app.callback(
        dash.Output('validate-modal', 'opened',   allow_duplicate=True),
        dash.Output('hikelist-div',   'children', allow_duplicate=True),
        dash.Output('number-hikes',   'data',     allow_duplicate=True),
        dash.Output('hikes-info',     'data',     allow_duplicate=True),
        dash.Output('map-polylines',  'children', allow_duplicate=True),

        dash.Input('validate-modal-yes', 'n_clicks'),
        dash.State('hikelist-div', 'children'),
        dash.State('hikes-info', 'data'),
        dash.State('map-polylines', 'children'),
        prevent_initial_call=True
    )
    def yes_button(
            _, 
            children   : list[dict], 
            hikes_info : dict[str, HikeInfo], 
            traces     : list[dict]
        ) -> tuple[typing.Literal[False], list[dict], int, dict[str, HikeInfo], list[dict]]:
        r'''
        Callback used when 'Yes' button is pressed.

        :param children: list of hike UI row elements in the hike panel
        :param hikes_info: dictionary containing information about each loaded hike
        :param traces: traces drawn on the map

        :returns: a tuple with
            - False
            - updated list of hike UI row elements for the hike panel with one hike removed
            - updated number of loaded hikes
            - updated dictionary with hike information
            - updated traces to draw on the map
        '''
        
        hike_name = session.pop('hike-to-delete')
        Hikes_table.delete_hike_from_db_given_name(hike_name)

        out_children   = []

        for child in children:

            if child['props']['id']['index'] != hike_name:
                out_children.append(child)

        # Remove the hike information from the dictionary
        hikes_info.pop(hike_name)

        # Remove the hike from the map
        traces = [trace for trace in traces if trace['props']['id']['index'] != hike_name]

        return False, out_children, len(out_children), hikes_info, traces

    return

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
        
        dash.Input('dummy', 'data'),
        dash.State('language', 'data'),

        prevent_initial_call=True
    )
    def secure_login_second_pass(
        dummy    : Dummy,
        language : LANGUAGE
        ) -> tuple[
            dl.Map, # map -> children
            list[Notification]  | dash.NoUpdate,

            tuple[str, str]     | tuple[dash.NoUpdate, dash.NoUpdate],
            tuple[str, str]     | tuple[dash.NoUpdate, dash.NoUpdate],
            
            list[dmc.Space]     | dash.NoUpdate,
            int                 | dash.NoUpdate,
            dict[str, HikeInfo] | dash.NoUpdate,

            list[dl.Polyline]   | dash.NoUpdate
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

        return (
            generate_leaflet_map_figure(),
            [login_success_notification(translation['notifications'])], 
            (username, username), (login_button_tooltip, login_button_tooltip),
            widgets, len(widgets), hikes_info, 
            traces
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

    return

def update_ui_after_single_hike_load(
        latitudes        : list[float],
        longitudes       : list[float],
        pos_absolute     : int,
        hike_name        : str,
        language_dict    : dict,
        magic_link_state : bool = False
    ) -> tuple[dmc.Space, dl.Polyline]:
    r'''
    Update components after a single hike load.

    :param latitudes: latitudes of the hike plotted on the map
    :param longitudes: longitudes of the hike plotted on the map
    :param pos_absolute: absolute index of the hike in the hike list
    :param hike_name: name of the hike
    :param language_dict: dictionary for the hikelist element
    :param magic_link_state: True triggers a special UI for magic links, False triggers the normal UI

    :returns:
        - hikelist element widget
        - PolyLine that represents the path of the hike
    '''

    color    = COLOR_PALETTE[pos_absolute]

    # Create a hike widget in the hike list
    widget   = hikelist_element_layout(
        hike_name,
        color,
        False if pos_absolute > 0 else True,
        language_dict,
        magic_link_state = magic_link_state
    )

    line = dl.Polyline(
        id          = {'type' : 'map-trace', 'index' : hike_name},
        positions   = [(la, lo) for lo, la in zip(longitudes, latitudes)],
        pathOptions = {'color' : color}
    )

    return widget, line

def update_ui_after_multiple_hike_loads(
    app              : dash.Dash,
    property_dict    : dict[str, HikeInfo],
    hike_widgets     : list,
    language         : LANGUAGE,
    magic_link_state : bool = False
) -> tuple[list[dmc.Space], list[dl.Polyline]]:
    r'''
    Generate the new UI components that must be updated after many new hike have been loaded.

    :param app: dash app
    :param property_dict: dictionary containing hike names as keys and dictionaries with hike properties as values
    :param hike_widgets: current widgets holding hikes in the hike list
    :param language_dict: dictionary for the hikelist element
    :param magic_link_state: True triggers a special UI for magic links, False triggers the normal UI

    :returns:
        - list of hike element widgets
        - list of hike traces for the map
    '''

    language_dict = app.language_handler[language]['hike_panel']
    pos_init      = len(hike_widgets)

    new_hike_widgets = []
    new_traces       = []

    for pos, (hike_name, properties) in enumerate(property_dict.items()):

        out = update_ui_after_single_hike_load(
            properties['latitudes'],
            properties['longitudes'],
            pos_init + pos,
            hike_name,
            language_dict,
            magic_link_state = magic_link_state
        )

        if out is None: continue

        new_hike_widgets.append(out[0])
        new_traces.append(out[1])

    hike_widgets.extend(new_hike_widgets)

    return hike_widgets, new_traces

def generate_hike_ui_elements_with_login(
        app      : dash.Dash, 
        language : LANGUAGE  
    ) -> tuple[dict[str, HikeInfo], list[dmc.Space], list[dl.Polyline]]:
    r'''
    Generate all the ui elements that need to be updated after login.

    :param app: dash app
    :param language: selected language

    :returns:
        - dictionary with hike information for each hike
        - list of hike element widgets
        - list of hike traces for the map
    '''

    # Query hikes database associated to the user
    hike_properties = execute_get_query(f'''
        SELECT name, latitude, longitude, center_lat, center_lon, distances, elevations
        FROM hikes
        WHERE user_id = '{session["user_id"]}';
    ''')

    # Build the dictionary with hike properties
    property_dict = {}

    for hike in hike_properties:

        inside_dict = HikeInfo(
            latitudes             = hike[1],
            longitudes            = hike[2],
            center_lat            = hike[3],
            center_lon            = hike[4],
            distances             = hike[5],
            elevations            = hike[6]
        )

        property_dict[hike[0]] = inside_dict

    widgets, traces = update_ui_after_multiple_hike_loads(
        app, property_dict, [],
        language,
        magic_link_state = session['magic-link']
    )

    return property_dict, widgets, traces

def generate_hike_ui_elements_with_hike_id(
        app      : dash.Dash, 
        language : LANGUAGE,
        hike_id  : int
    ) -> tuple[dict[str, HikeInfo], list[dmc.Space], list[dl.Polyline]]:
    r'''
    Generate all the ui elements that need to be updated if a single hike ID is provided.

    :param app: dash app
    :param language: selected language

    :returns:
        - dictionary with hike information for each hike
        - list of hike element widgets
        - list of hike traces for the map
    '''

    # Query hikes database associated to the user
    hike_properties = execute_get_query(f'''
        SELECT name, latitude, longitude, center_lat, center_lon, distances, elevations
        FROM hikes
        WHERE id = {hike_id};
    ''')

    # Build the dictionary with hike properties
    property_dict = {}

    for hike in hike_properties:

        inside_dict = HikeInfo(
            latitudes             = hike[1],
            longitudes            = hike[2],
            center_lat            = hike[3],
            center_lon            = hike[4],
            distances             = hike[5],
            elevations            = hike[6]
        )

        property_dict[hike[0]] = inside_dict

    widgets, traces = update_ui_after_multiple_hike_loads(
        app, property_dict, [],
        language,
        magic_link_state = session['magic-link']
    )

    return property_dict, widgets, traces