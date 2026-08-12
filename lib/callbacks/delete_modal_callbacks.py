import dash
import typing
from   flask import session

from ..types    import HikeInfo
from ..database import Hikes_table

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