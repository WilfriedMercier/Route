import dash
import dash_leaflet            as     dl
import dash_mantine_components as     dmc
from   flask                   import session

from .misc            import update_ui_after_multiple_hike_loads
from ..components.map import generate_leaflet_map_figure
from ..lang           import LANGUAGE
from ..errors         import UnsupportedFileFormatError
from ..database       import Hikes_table
from ..misc           import check_if_hike_is_loaded, COLOR_PALETTE
from ..io             import decode_and_process_uploaded_file

from ..types          import (
    DummyWithTraces, 
    Notification, 
    HikeInfo, 
    MultiselectData, 
    MultiselectDataRow
)

from ..components.notifications import (
    hike_upload_success_notification,
    hike_upload_format_fail_notification,
    hike_upload_already_there_fail_notification
)

def register_upload_hike_callbacks(app: dash.Dash) -> None:
    r'''All callbacks associated to uploading hikes.'''

    @app.callback(
        dash.Output('map-div', 'children', allow_duplicate=True),
        dash.Output('map-polylines', 'children', allow_duplicate=True),
        dash.Input('dummy-with-traces', 'data'),
        prevent_initial_call=True
    )
    def upload_hike_second_pass(dummy: DummyWithTraces) -> tuple[dl.Map, list[dl.Polyline]]:
        r'''
        Second pass of the hike upload that updates the figure.

        :param dummy: a dummy object containing the traces to add on the map

        :returns: a tuple with
            - an empty map
            - traces to add to the map
        '''

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
        dash.Output({'type' : 'magic-link-multiselect', 'index' : dash.ALL}, 'data', allow_duplicate=True),
        
        dash.Input('upload-hike-button', 'contents'),
        dash.State('upload-hike-button', 'filename'),
        dash.State('hikelist-div', 'children'),
        dash.State('map-polylines', 'children'),
        dash.State('language', 'data'),
        dash.State('hikes-info', 'data'),
        dash.State('dummy-with-traces', 'data'),
        dash.State({'type' : 'magic-link-multiselect', 'index' : dash.ALL}, 'data'),
        prevent_initial_call = True
    )
    def upload_hike_first_pass(
        file_contents    : list[str] | None, 
        filenames        : list[str], 
        hike_widgets     : list[dmc.Space],
        traces           : list[dl.Polyline],
        language         : LANGUAGE,
        hikes_info       : dict[str, HikeInfo],
        dummy            : DummyWithTraces,
        multiselect_data : list[MultiselectData]
    ) -> tuple[
            list[dmc.Space]     | dash.NoUpdate, 
            int                 | dash.NoUpdate, 
            dict[str, HikeInfo] | dash.NoUpdate,
            list[Notification],
            dict[str, str]      | dash.NoUpdate,
            dict[str, str]      | dash.NoUpdate,
            DummyWithTraces     | dash.NoUpdate,
            list[MultiselectData]
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
        :param multiselect_data: data values for all the multiselect components in the magic link panel

        :returns:
            - updated list of hike widgets
            - updated number of hikes
            - updated `HikeInfo` object
            - notification to send if any
            - dictionary indicating whether the elevation plot should be visible or not
            - dictionary indicating the height of the map
            - dummy object containing the traces used to trigger the second rendering pass
            - updated multiselect data for all components
        '''

        if file_contents is None or len(file_contents) == 0: raise dash.exceptions.PreventUpdate


        translation = app.language_handler[language]['notifications']

        # Number of widgets currently displayed
        n_widgets = len(hike_widgets)

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

        for pos, (content, filename) in enumerate(zip(file_contents, filenames)):

            pos_absolute = n_widgets + pos

            try: 

                hike_name, properties = decode_and_process_uploaded_file(content, filename)
                properties['color']   = COLOR_PALETTE[pos_absolute]

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

            multiselect_row = MultiselectDataRow(
                value = hike_name,
                label = hike_name
            )

            multiselect_data = [m + [multiselect_row] for m in multiselect_data]

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
            out_dummy, multiselect_data
        )