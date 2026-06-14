import dash
import dash_mantine_components as     dmc
from   dash_iconify            import DashIconify

class MenuBar:

    def __init__(self, app: dash.Dash) -> None:

        self._app = app

        self._init_layout()
        self._register_callbacks()

        return
    
    @property
    def app(self) -> dash.Dash: return self._app
    
    @property
    def layout(self) -> dmc.Stack: return self._layout

    @property
    def hike_panel_button(self) -> dmc.Button: return self._hike_panel_button
    
    @property
    def hall_of_fame_button(self) -> dmc.Button: return self._hall_of_fame_button

    def _init_layout(self) -> None:

        self._hike_panel_button = dmc.Button(
            DashIconify(icon='gis:hiker'),
            id = 'hike-panel-button',
        )

        self._hall_of_fame_button = dmc.Button(
            DashIconify(icon='mdi:achievement-outline'),
            id = 'hof-button'
        )

        self._layout = dmc.Stack(
            [self.hike_panel_button, self.hall_of_fame_button],
            id = 'menubar'
        )

        return
    
    def _register_callbacks(self) -> None:

        @self.app.callback(
            dash.Output('hike-panel', 'opened'),
            dash.Input('hike-panel-button', 'n_clicks'),
            prevent_initial_call=True
        )
        def hike_panel_button_callback(n_clicks: int | None) -> bool:

            print('hey')

            if n_clicks is None: return False

            return True
        
        return