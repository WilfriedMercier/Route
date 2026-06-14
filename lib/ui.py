import dash
import dash_mantine_components as     dmc
import plotly.graph_objects    as     go
from   typing                  import Any

from   .io                    import load_hikes_from_directory
from   .lang                  import LanguageEnum, map_string_code_to_language
from   .components            import TopBar, HikePanel, MapPage, MenuBar

class UI:
    r'''
    Class responsible for building the user interface of the application.
    
    :param app: The Dash application instance.
    :param translations: A dictionary containing translations for different languages.
    :param default_language: default language used when the application starts
    '''

    def __init__(
            self, 
            app              : dash.Dash, 
            translations     : dict[str, dict], 
            default_language : LanguageEnum
        ) -> None:

        self.app               = app

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

        self._init_layout(
            center_lat, center_lon, zoom,
            translations, default_language,
            color
        )

        self.map_page.map.add_hikes_to_map(self.hikes_data)
        self.map_page.elevation_plot.add_elevation_data_to_plot(distances, elevations, color)

        self._register_callbacks()

        return
    
    @property
    def map_page(self) -> MapPage: 
        '''Main page containing the hike and elevation maps.'''

        return self._map_page
    
    @property
    def topbar(self) -> TopBar:
        '''Bar at the top of the page.'''

        return self._topbar
    
    @property
    def menubar(self) -> MenuBar: 
        '''Menu bar located at the right or the bottom of the page.'''

        return self._menubar
    
    @property
    def hike_panel(self) -> HikePanel:
        '''Hike panel shown when the right button is clicked in the menu bar.'''

        return self._hike_panel
    
    @property
    def layout(self) -> dmc.Stack: return self._layout
    
    def _init_layout(
            self, 
            center_lat       : float, 
            center_lon       : float,
            zoom             : int,
            translations     : dict[str, dict],
            default_language : LanguageEnum,
            color            : str   
        ) -> None:
        r'''Build the main layout of the application.'''

        self._topbar       = TopBar(
            self.app,
            {lang : translation['topbar'] for lang, translation in translations.items()}, 
            default_language
        )

        self._map_page = MapPage(center_lat, center_lon, zoom, translations, default_language, color)
        
        self._hike_panel = HikePanel(
            self.app,
            {hike_name : {'color' : properties['color']} for hike_name, properties in self.hikes_data.items()},
            {lang : translation['hike_panel'] for lang, translation in translations.items()}, 
            default_language
        )

        self._menubar = MenuBar(self.app)

        self._layout = dmc.Stack(
            [
                self.topbar.layout, 
                dmc.Group(
                    [
                        self.map_page.layout,
                        self.menubar.layout,
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
                    mapbox=dict(
                        center=dict(lat=self.map_page.map.center[0], lon=self.map_page.map.center[1]),
                        zoom=self.map_page.map.zoom
                    )
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
                mapbox=dict(
                    center=dict(lat=self.map_page.map.center[0], lon=self.map_page.map.center[1]),
                    zoom=self.map_page.map.zoom
                )
            )

            return self.map_page.map.fig
        
        @self.app.callback(
                [
                    dash.Output('map', 'figure', allow_duplicate=True),
                    dash.Output('theme-toggle-tooltip', 'label')
                ],
            #Output('sidebar-collapsible-content', 'children'),
            dash.Input('language-dropdown', 'value'),
            prevent_initial_call=True
        )
        def language_selection_callback(
            value: str | None
        ) -> tuple[go.Figure, Any] | tuple[dash.NoUpdate, dash.NoUpdate]:

            if value is None: 
                return dash.no_update, dash.no_update

            # Value in the dropdown must be a string so we parse it to the right type
            lang = map_string_code_to_language(value)

            self.topbar.update_layout_language(lang)
            self.hike_panel.update_layout_language(lang)
            self.map_page.elevation_plot.update_layout_language(lang)

            return (
                self.map_page.map.fig, 
                self.topbar.language_handler['theme_switcher']['tooltip']
            )
                
