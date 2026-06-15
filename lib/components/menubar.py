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

    def _init_layout(self) -> None:

        hike_panel_button = dmc.Button(
            DashIconify(icon='gis:hiker', height=28, width=28),
            id        = 'hike-panel-button',
            size      = 'lg',
            variant   = 'outline',
            className = 'menubar-button',
        )

        hike_panel_button_tooltip = dmc.Tooltip(
            hike_panel_button,
            label     = self.app.lang['menubar']['hike_panel_button']['tooltip'],
            openDelay = 1000,
            id        = 'hike-panel-button-tooltip'
        )

        hall_of_fame_button = dmc.Button(
            DashIconify(icon='mdi:achievement-outline', height=28, width=28),
            id        = 'hof-button',
            size      = 'lg',
            variant   = 'outline',
            className = 'menubar-button',
            disabled  = True
        )

        hall_of_fame_button_tooltip = dmc.Tooltip(
            hall_of_fame_button,
            label    = self.app.lang['menubar']['hall_of_fame_button']['tooltip'],
            disabled = True,
            id       = 'hall-of-fame-button-tooltip'
        )

        self._layout = dmc.Stack(
            [hike_panel_button_tooltip, hall_of_fame_button_tooltip],
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

            if n_clicks is None: return False

            return True
        
        return