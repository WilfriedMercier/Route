import dash_mantine_components as     dmc
from   dash_iconify            import DashIconify

class MenuBar:

    def __init__(self) -> None:

        self._init_layout()

        return
    
    @property
    def layout(self) -> dmc.Stack: return self._layout

    @property
    def hike_panel_button(self) -> dmc.Button: return self._hike_panel_button
    
    @property
    def hall_of_fame_button(self) -> dmc.Button: return self._hall_of_fame_button

    def _init_layout(self) -> None:

        self._hike_panel_button = dmc.Button(
            DashIconify(icon='gis:hiker'),
            id = 'hike-pannel-button',
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