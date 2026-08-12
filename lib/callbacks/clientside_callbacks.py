import dash

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