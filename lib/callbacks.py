import dash
import typing
import plotly.graph_objects    as     go
import numpy                   as     np

from flask         import session

from .types import (
    HikeProps, 
    HikeInfo,
    HikeDataForElevationPlot,
    EMPTY_HIKE_DATA_FOR_PLOT
)

from .lang       import LANGUAGE

from .components.map         import generate_new_figure
from .database               import (
    Hikes_table
)

def register_callbacks(app : dash.Dash) -> None:
    r'''
    Register all callbacks.

    :param app: dash application
    '''

    return



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
