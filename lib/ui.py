import dash
import dash_mantine_components as     dmc
import plotly.graph_objects    as     go
from   typing                  import Any

from   .lang                   import LanguageEnum
from   .io                     import load_hikes_from_directory
from   .components             import TopBar, HikePanel, MapPage, MenuBar

class UI:
    r'''
    Class responsible for building the user interface of the application.
    
    :param app: The Dash application instance
    '''

    def __init__(self, app : dash.Dash) -> None:

        self._app              = app

        self.hikes_data        = load_hikes_from_directory()
        self.current_hike_name = next(iter(self.hikes_data.keys()), None)
        current_hike           = self.hikes_data[self.current_hike_name] if self.current_hike_name else None

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

        self._init_layout(center_lat, center_lon, zoom, color)

        self._map_page.map.add_hikes_to_map(self.hikes_data)
        self._map_page.elevation_plot.add_elevation_data_to_plot(distances, elevations, color)

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
            center_lat       : float, 
            center_lon       : float,
            zoom             : int,
            color            : str   
        ) -> None:
        r'''Build the main layout of the application.'''

        topbar    = TopBar(self.app)

        self._map_page  = MapPage(self.app, center_lat, center_lon, zoom, color)
        
        self._hike_panel = HikePanel(
            self.app,
            {hike_name : {'color' : properties['color']} for hike_name, properties in self.hikes_data.items()}
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
            dash.Output('map', 'figure', allow_duplicate=True),
            dash.Input('elevation-plot', 'hoverData'),
            prevent_initial_call=True,
        )
        def hovered_point_callback(hoverData: dict) -> go.Figure:
            r'''Callback to update the display when a point is hovered on the elevation plot.'''
            
            if hoverData is None or self.current_hike_name is None: return self.map_page.map.fig

            index  = hoverData['points'][0]['pointIndex']
            coords = self.hikes_data[self.current_hike_name]['coords'][index]

            for trace in self.map_page.map.fig.data:

                if trace is None: continue
                elif trace.name == 'point': # type: ignore
                    trace.lat = [coords[0]] # type: ignore
                    trace.lon = [coords[1]] # type: ignore

                    break

                self.map_page.map.fig.update_layout(
                    mapbox = {
                        'center' : {
                            'lat' : self.map_page.map.center[0], 
                            'lon' : self.map_page.map.center[1]
                        },
                        'zoom' : self.map_page.map.zoom
                    }
                )

            return self.map_page.map.fig
        
        @self.app.callback(
            dash.Output('map', 'figure', allow_duplicate=True),
            dash.Input('map', 'relayoutData'),
            prevent_initial_call=True
        )
        def map_interaction_callback(relayoutData: dict) -> go.Figure:
            r'''Callback triggered every time the user pans or zooms the map.'''
            
            if relayoutData is None or 'mapbox.center' not in relayoutData or 'mapbox.zoom' not in relayoutData: 
                return self.map_page.map.fig
            
            # Update the map's center and zoom level based on the user's interaction
            self.map_page.map.center = (relayoutData['mapbox.center']['lat'], relayoutData['mapbox.center']['lon'])
            self.map_page.map.zoom   = relayoutData['mapbox.zoom']
            
            # This callback is triggered on any pan/zoom event
            self.map_page.map.fig.update_layout(
                mapbox = {
                    'center' : {
                        'lat' : self.map_page.map.center[0], 
                        'lon' : self.map_page.map.center[1]
                    },
                    'zoom' : self.map_page.map.zoom
                }
            )

            return self.map_page.map.fig
        
        @self.app.callback(
                [
                    dash.Output('theme-toggle-tooltip', 'label'),
                    dash.Output('hike-panel-button-tooltip', 'label'),
                    dash.Output('hall-of-fame-button-tooltip', 'label'),
                    dash.Output('hike-panel', 'title'),
                    dash.Output({'type' : 'hikelist-hide-button-tooltip', 'index' : dash.ALL}, 'label'),
                    dash.Output({'type' : 'hikelist-colorpicker-tooltip', 'index' : dash.ALL}, 'label')
                ],
            dash.Input('language-dropdown', 'value'),
            prevent_initial_call=True
        )
        def language_selection_callback(
            value: str
        ) -> tuple[str, str, str, str, list[str], list[str]]:

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
                [self.app.lang['hike_panel']['colorpicker']['tooltip']] * n_buttons
            )