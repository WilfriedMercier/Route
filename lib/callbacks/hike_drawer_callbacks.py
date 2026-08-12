import dash
import typing
import plotly.graph_objects as     go
import numpy                as     np
from   flask                import session

from ..database       import Hikes_table, Magic_links_table
from ..components.map import generate_new_figure
from ..lang           import LANGUAGE
from ..errors         import NoHikeIDInDB, NoMagicLinkForHikeID
from ..types import (
    HikeInfo, 
    HikeProps, 
    HikeDataForElevationPlot, 
    HikeDataForMarker,
)

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