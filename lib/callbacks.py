import dash
import plotly.graph_objects as go
from   urllib.parse import urlparse, parse_qs

from   .lang        import LanguageEnum, LanguageHandler
from   .io          import load_hikes_from_directory
from   .components  import ui_layout

def register_callbacks(
        app              : dash.Dash, 
        language_handler : LanguageHandler,
        token_db         : dict
    ) -> None:

    """
    @app.callback(
        [
            dash.Output('content-display', 'children'),
            dash.Output('number_hikes', 'data')
        ],
        dash.Input('url', 'href')
    )
    def render_ui(url: str) -> tuple[dash.html.Div, int]:

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
    """
    
    @app.callback(
        [
            dash.Output('theme-toggle-tooltip', 'label'),
            dash.Output('hike-panel-button-tooltip', 'label'),
            dash.Output('hall-of-fame-button-tooltip', 'label'),
            dash.Output('hike-panel', 'title'),
            dash.Output({'type' : 'hikelist-hide-button-tooltip',  'index' : dash.ALL}, 'label'),
            dash.Output({'type' : 'hikelist-colorpicker-tooltip',  'index' : dash.ALL}, 'label'),
            dash.Output({'type' : 'hikelist-share-button-tooltip', 'index' : dash.ALL}, 'label')
        ],
        dash.Input('language-dropdown', 'value'),
        dash.State('number_hikes', 'data'),
        prevent_initial_call=True,
    )
    def language_selection_callback(value: str, n_hikes: int) -> tuple[str, str, str, str, list[str], list[str], list[str]]:

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
            [language_handler['hike_panel']['share_button']['tooltip']] * n_hikes
        )

    @app.callback(
        dash.Output('hike-panel', 'opened'),
        dash.Input('hike-panel-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def hike_panel_button_callback(n_clicks: int | None) -> bool:

        if n_clicks is None: return False

        return True

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
    def hike_button_callback(
        _, n_hikes: int, hikes_info: dict, map_dict: dict
    ) -> tuple[list[dict[str, str]] | list[dash.NoUpdate], go.Figure | dash.NoUpdate]:


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
    def colorpicker_callback(colors: str, map_dict: dict) -> go.Figure | dash.NoUpdate:
        '''
        Callback called whenever the given colorpicker is clicked.
        
        :param color: color selected by the colorpicker
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
    def hide_button_callback(
        checked_list: list[bool], map_dict: dict, colors: list[str], number_hikes: int
    ) -> (
            tuple[list[bool], list[bool], list[bool], go.Figure] | 
            tuple[list[dash.NoUpdate], list[dash.NoUpdate], list[dash.NoUpdate], dash.NoUpdate]
        ):
        r'''
        Callback used when the hide button is toggled.

        :param checked: whether the hide buttons are checked
        :param map_dict: current layout for the map
        :param color: current color of each colorpicker
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

    @app.callback(
        dash.Output('map', 'figure', allow_duplicate = True),
        dash.Input({'type' : 'map-style-button', 'index' : dash.ALL}, 'n_clicks'),
        dash.State('map', 'figure'),
        prevent_initial_call = True
    )
    def callback_map_style_change_from_button(_, map_dict: go.Figure) -> go.Figure | dash.NoUpdate:

        ctx = dash.callback_context# Extract the ID of the clicked button

        if ctx is None or not ctx.triggered: return dash.no_update

        clicked_index = ctx.triggered_id['index'] # type: ignore

        figure = go.Figure(map_dict)
        figure.update_layout(
            mapbox = {'style' : clicked_index}
        )

        return figure

    return