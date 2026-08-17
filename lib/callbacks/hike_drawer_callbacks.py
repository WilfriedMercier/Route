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
    DashComplexID,
    HikeInfo, 
    HikeProps, 
    HikeDataForElevationPlot, 
    HikeDataForMarker,
    EMPTY_HIKE_DATA_FOR_PLOT
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

        dash.Output('elevation-plot', 'figure'),

        dash.Output('elevation-plot-slider', 'max'),

        dash.Input( {'type' : 'hikelist-button', 'index' : dash.ALL}, 'n_clicks'),
        dash.State('hikes-info', 'data'),
        dash.State({'type' : 'hikelist-colorpicker-button', 'index' : dash.ALL}, 'color'),
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
            fig, len(info['distances'])
        )

    @app.callback(
        dash.Output({'type' : 'hikelist-button',               'index' : dash.MATCH}, 'disabled'),
        dash.Output({'type' : 'hikelist-colorpicker-button',   'index' : dash.MATCH}, 'disabled'),
        dash.Output({'type' : 'hikelist-colorpicker-popover',  'index' : dash.MATCH}, 'disabled'),
        dash.Output({'type' : 'hikelist-colorpicker-tooltip',  'index' : dash.MATCH}, 'disabled'),
        dash.Output({'type' : 'map-trace',                     'index' : dash.MATCH}, 'pathOptions', allow_duplicate=True),

        dash.Input({'type' : 'hikelist-hide-button', 'index' : dash.MATCH}, 'checked'),
        dash.State({'type' : 'hikelist-colorpicker-button', 'index' : dash.MATCH}, 'color'),

        prevent_initial_call = True
    )
    def hide_button(
        checked : bool,
        color   : str,
    ) -> tuple[bool, bool, bool, bool, dict]:
        r'''
        Callback used when the hide button is toggled.

        :param checked: whether the hide button is checked
        :param color: current color for the colorpicker button

        :returns: a tuple containing
            - 4 times the same True or False value for each hike wiget UI element (True to disable, False to enable)
            - a dictionary inside specifying the color of the line on the map (transparent if hidden)
        '''

        output     = not checked

        # Change disabled hikes color to transparent
        hike_color = {'color' : color if checked else 'rgba(0, 0, 0, 0)'}

        return output, output, output, output, hike_color
    
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

    @app.callback(
        dash.Output({'type' : 'hikelist-colorpicker-button',  'index' : dash.ALL}, 'color'),
        dash.Output('selected-hike-props', 'data', allow_duplicate=True),
        dash.Output({'type' : 'map-trace', 'index' : dash.ALL}, 'pathOptions', allow_duplicate=True),
        dash.Output('elevation-plot', 'figure', allow_duplicate=True),

        dash.Input({'type' : 'hikelist-colorpicker-picker',  'index' : dash.MATCH}, 'value'),
        dash.State({'type' : 'hikelist-colorpicker-picker',  'index' : dash.ALL},   'id'),
        dash.State('selected-hike-props', 'data'),
        dash.State('selected-hike-data-for-plot', 'data'),
        dash.State('language', 'data'),

        prevent_initial_call=True
    )
    def colorpicker_selection(
            selected_color  : str | None,
            all_ids         : list[DashComplexID],
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
        :param hike_props: properties associated to the clicked colorpicker button
        :param dist_elev: object containing distance and elevation data for the elevation plot
        :param language: current language of the UI

        :returns:
            - color (or dash.no_update) for the colorpicker button
            - dictionary with properties associated to the hike. The color information is updated
            - list of dictionaries with updated colors for the map
            - figure for the elevation plot with an updated color if it corresponds to the currently selected hike. Otherwise dash.no_update
        '''

        triggered_id = dash.ctx.triggered_id

        if triggered_id is None: raise dash.exceptions.PreventUpdate

        hike_name = triggered_id['index']

        # If data is missing, we prevent any update
        if (
            selected_color is None or
            hike_name == '' or 
            hike_props == {} or 
            dist_elev == EMPTY_HIKE_DATA_FOR_PLOT
        ): raise dash.exceptions.PreventUpdate
        
        # If the user is changing the color of the selected hike, we update the color attribute in the Store
        if hike_props['name'] == hike_name: 
            hike_props['color'] = selected_color

        # If the index of the changed color does not match the selected hike, we do not update the elevation plot color
        if hike_name != hike_props['name']:
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
            {'color' : selected_color} if triggered_id == hike_id
            else dash.no_update
            for hike_id in all_ids
        ]

        colors = [selected_color if triggered_id == hike_id else dash.no_update for hike_id in all_ids]

        # Update the color of the hike in the database
        hike_id = Hikes_table.get_hike_id_from_name(triggered_id['index'])

        Hikes_table.update_color_in_row(selected_color, hike_id)

        return colors, hike_props, map_props, fig
    
    return