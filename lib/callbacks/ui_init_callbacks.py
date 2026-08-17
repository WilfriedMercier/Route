import typing
import dash
import dash_leaflet            as     dl
import dash_mantine_components as     dmc
from   flask                   import session
from   urllib.parse            import urlparse, parse_qs

from .misc                      import (
    generate_magic_link_container_rows_from_db,
    generate_hike_ui_elements_with_login, 
    generate_hike_ui_elements_with_hike_id
)

from ..lang                     import LANGUAGE
from ..errors                   import NoHikeForMagicLink
from ..components.notifications import wrong_magic_link_notification
from ..components.map           import generate_leaflet_map_figure
from ..database                 import Users_table, Magic_links_props_table
from ..types                    import HikeInfo, Notification

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
    def render_ui_first_pass(url: str) -> tuple[
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
        dash.Output('magic-link-button',      'disabled',          allow_duplicate=True),
        dash.Output('magic-link-button-tooltip', 'disabled',       allow_duplicate=True),
        dash.Output('magic-link-container',   'children',          allow_duplicate=True),

        dash.Input('magic-link', 'data'),
        dash.State('language', 'data'),
        dash.State('base-url', 'data'),

        prevent_initial_call = True
    )
    def render_ui_second_pass(
            magic_link :  str | None,
            language   : LANGUAGE,
            base_url   : str
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
            bool, # magic-link-button -> disabled
            bool, # magic-link-button-tooltip -> disabled
            list[dmc.Stack] | dash.NoUpdate
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
        # - magic link panel button
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
                    dash.no_update,  dash.no_update, [notification],
                    True, True,
                    dash.no_update
                )

            # Case when magic link is correct
            return (
                generate_leaflet_map_figure(),
                ({'display' : 'none'}, {'display' : 'none'}),
                (dash.no_update, dash.no_update),
                (dash.no_update, dash.no_update),
                widgets, n_hikes, hikes_info, traces,
                {'display' : 'flex'},  {'display' : 'none'}, dash.no_update,
                True, True,
                dash.no_update
            )
        
        # Case without a magic link
        else:

            (
                button_style_1, button_style_2,
                widgets, n_hikes, hikes_info, traces,
                login_button, login_tooltip
            ) = handle_without_magic_link(language)

            # Generate the container items for the magic link panel
            children = generate_magic_link_container_rows_from_db(
                app.language_handler[language]['magic_link_panel'],
                list(hikes_info.keys()),
                base_url=base_url
            )

            return (
                generate_leaflet_map_figure(),
                (button_style_1, button_style_2), 
                (login_button, login_button),
                (login_tooltip, login_tooltip),
                widgets, n_hikes, hikes_info, traces,
                {'display' : 'flex' if 'user_id' in session else 'none'}, 
                dash.no_update, dash.no_update,
                'user_id' not in session,
                'user_id' not in session,
                children
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

        # Get the hike IDs associated to the magic link. If None, no link 
        hike_ids = Magic_links_props_table.get_hike_ids_from_magic_link(magic_link)

        hikes_info, widgets, traces = generate_hike_ui_elements_with_hike_id(
            app, language, hike_ids, magic_link
        )

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

        # XXX to be removed
        #session['user_id'] = Users_table.get_user_id_from_username('wilfried')

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