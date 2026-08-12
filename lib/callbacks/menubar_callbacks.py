import dash
import typing

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

    @app.callback(
        dash.Output('magic-link-panel', 'opened'),
        dash.Input('magic-link-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def magic_link_button_click(_) -> typing.Literal[True]:
        r'''Callback used when the magic link panel button is clicked.'''

        if _ is None: dash.exceptions.PreventUpdate

        return True
    
    return