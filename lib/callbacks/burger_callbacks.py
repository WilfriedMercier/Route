import dash
import typing

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