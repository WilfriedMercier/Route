import dash
import dash_mantine_components as     dmc
import plotly.graph_objects    as     go
from   typing                  import Any

from   .lang                   import LanguageEnum
from   .io                     import load_hikes_from_directory
from   .components             import BaseWidget, TopBar, HikePanel, MapPage, MenuBar

class UI(BaseWidget):
    r'''
    Class responsible for building the user interface of the application.
    
    :param app: The Dash application instance
    :param hikes_data: dictionary containing the hike information to display
    '''

    def __init__(self, app : dash.Dash, hikes_data: dict) -> None:

        super().__init__(app)

        current_hike_name = next(iter(hikes_data.keys()), None)
        current_hike      = hikes_data[current_hike_name] if current_hike_name else None

        if current_hike is not None:
            center_lat, center_lon = current_hike['center']
            zoom                   = current_hike['zoom']
            distances              = current_hike['distances']
            elevations             = current_hike['elevations']
            color                  = current_hike['color']
        else:
            center_lat, center_lon, zoom = 45.7640, 4.8357, 10  # Default to Lyon if no hikes are loaded
            distances, elevations        = [], []
            color                        = 'black'

        self._init_layout(hikes_data, center_lat, center_lon, zoom, color)

        self.map_page.map.add_hikes_to_map(hikes_data)
        self.map_page.elevation_plot.add_elevation_data_to_plot(distances, elevations, color)

        self._register_callbacks()

        return
    
    @property
    def app(self) -> dash.Dash: return self._app
    
    @property
    def layout(self) -> dmc.Stack: return self._layout

    @property
    def map_page(self) -> MapPage: return self._map_page
    
    @property
    def hike_panel(self) -> HikePanel: return self._hike_panel

    def _init_layout(
            self, 
            hikes_data : dict,
            center_lat : float, 
            center_lon : float,
            zoom       : int,
            color      : str   
        ) -> None:
        r'''Build the main layout of the application.'''

        topbar    = TopBar(self.app)

        self._map_page  = MapPage(self.app, center_lat, center_lon, zoom, color)
        
        self._hike_panel = HikePanel(
            self.app,
            {hike_name : {'color' : properties['color']} for hike_name, properties in hikes_data.items()}
        )

        menubar = MenuBar(self.app)

        self._layout = dmc.Stack(
            [
                topbar.layout, 
                dmc.Group(
                    [
                        self.map_page.layout,
                        menubar.layout,
                        self.hike_panel.layout
                    ],
                    id = 'main-group'
                )
            ],
            id = 'main-stack',
        )

        return

    def _register_callbacks(self) -> None:
        
        @self.app.callback(
                [
                    dash.Output('theme-toggle-tooltip', 'label'),
                    dash.Output('hike-panel-button-tooltip', 'label'),
                    dash.Output('hall-of-fame-button-tooltip', 'label'),
                    dash.Output('hike-panel', 'title'),
                    dash.Output({'type' : 'hikelist-hide-button-tooltip',  'index' : dash.ALL}, 'label'),
                    dash.Output({'type' : 'hikelist-colorpicker-tooltip',  'index' : dash.ALL}, 'label'),
                    dash.Output({'type' : 'hikelist-share-button-tooltip', 'index' : dash.ALL}, 'label')
                ],
            dash.Input('language-dropdown', 'value'),
            prevent_initial_call=True
        )
        def language_selection_callback(
            value: str
        ) -> tuple[str, str, str, str, list[str], list[str], list[str]]:

            # Value in the dropdown is a string so we parse it to the right type
            lang = LanguageEnum.map_string_code_to_language(value)

            # Update the language of the language handler object
            self.app.lang.language = lang

            #self.map_page.elevation_plot.update_layout_language(lang)

            n_buttons = len(self.hike_panel.hike_list.buttons)

            return (
                self.app.lang['topbar']['theme_switcher']['tooltip'],
                self.app.lang['menubar']['hike_panel_button']['tooltip'],
                self.app.lang['menubar']['hall_of_fame_button']['tooltip'],
                self.app.lang['hike_panel']['title'],
                [self.app.lang['hike_panel']['hide_button']['tooltip']] * n_buttons,
                [self.app.lang['hike_panel']['colorpicker']['tooltip']] * n_buttons,
                [self.app.lang['hike_panel']['share_button']['tooltip']] * n_buttons
            )