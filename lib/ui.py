import dash
import plotly.graph_objects      as     go
import dash_bootstrap_components as     dbc
from   dash                      import html, dcc, Input, Output, State
from   typing                    import Any

from   .io                       import load_hikes_from_directory
from   .lang                     import LanguageEnum, LanguageHandler, map_string_code_to_language
from   .components               import TopBar, Sidebar

class UI:
    r'''
    Class responsible for building the user interface of the application.
    
    :param app: The Dash application instance.
    :param translations: A dictionary containing translations for different languages.
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

        # Defining the different UI components
        self.topbar       = TopBar(
            self.app,
            {lang : translation['topbar'] for lang, translation in translations.items()}, 
            default_language
        )

        map               = Map(center_lat, center_lon, zoom)
        elevation_plot    = ElevationPlot(
            {lang : translation['elevation_plot'] for lang, translation in translations.items()}, 
            default_language,
            color = color
        )

        self.main_content = MainContent(map, elevation_plot)
        self.sidebar      = Sidebar(
            self.app,
            {hike_name : {'color' : properties['color']} for hike_name, properties in self.hikes_data.items()},
            {lang : translation['sidebar'] for lang, translation in translations.items()}, 
            default_language
        )

        self.main_content.map.add_hikes_to_map(self.hikes_data)
        self.main_content.elevation_plot.add_elevation_data_to_plot(distances, elevations)

        self._build_layout()
        self._register_callbacks()

        return
    
    def _build_layout(self) -> None:
        r'''Build the main layout of the application.'''

        # Place the topbar at the top, and put sidebar + main content in a row below it
        self.layout = html.Div(
            [
                dcc.Store('theme', storage_type='local', data={'value' : 'light'}),
                self.topbar.layout,
                html.Div(
                    [
                        self.sidebar.layout,
                        self.main_content.layout
                    ],
                    className='d-flex',
                    style={
                        'display': 'flex',          # Enables flexbox
                        'height': '100vh',          # Full viewport height
                        'width': '100%',            # Full width
                        'overflow': 'hidden'        # Prevents double scrollbars
                    }
                )
            ],
            className='d-flex flex-column',
            style={
                'display': 'flex',          # Enables flexbox
                'height': '100vh',          # Full viewport height
                'width': '100%',            # Full width
                'overflow': 'hidden'        # Prevents double scrollbars
            },
        )

        return

    def _register_callbacks(self) -> None:

        """
        @self.app.callback(
            Output('map', 'figure'),
            Output('elevation-plot', 'figure'),
            Input('hike-list', "value")
        )
        def selected_hike_callback(hike_name: str | None) -> tuple[go.Figure, go.Figure]:
            r'''Callback to update the display when a hike is selected from the sidebar.'''
            
            if hike_name is None:
                return self.main_content.map.fig, self.main_content.elevation_plot.fig

            # Update the center and zoom of the map based on the selected hike
            hike_data              = self.hikes_data[hike_name]
            center_lat, center_lon = hike_data['center']
            zoom                   = hike_data['zoom']

            self.main_content.map.fig.update_layout(
                mapbox=dict(
                    center=dict(lat=center_lat, lon=center_lon),
                    zoom=zoom
                )
            )

            # Update the elevation plot with the data from the selected hike
            self.main_content.elevation_plot.add_elevation_data_to_plot(
                hike_data['distances'],
                hike_data['elevations']
            )

            # Save the currently selected hike name for use in the hover callback
            self.current_hike_name = hike_name

            for trace in self.main_content.map.fig.data:

                if trace is None: continue
                elif trace.name == 'point': # type: ignore
                    trace.lat = [] # type: ignore
                    trace.lon = [] # type: ignore

                    break

            return self.main_content.map.fig, self.main_content.elevation_plot.fig
        """
        @self.app.callback(
            Output('map', 'figure', allow_duplicate=True),
            Input('elevation-plot', 'hoverData'),
            prevent_initial_call=True,
        )
        def hovered_point_callback(hoverData: dict) -> go.Figure:
            r'''Callback to update the display when a point is hovered on the elevation plot.'''
            
            if hoverData is None or self.current_hike_name is None: return self.main_content.map.fig

            index  = hoverData['points'][0]['pointIndex']
            coords = self.hikes_data[self.current_hike_name]['coords'][index]

            for trace in self.main_content.map.fig.data:

                if trace is None: continue
                elif trace.name == 'point': # type: ignore
                    trace.lat = [coords[0]] # type: ignore
                    trace.lon = [coords[1]] # type: ignore

                    break

                self.main_content.map.fig.update_layout(
                    mapbox=dict(
                        center=dict(lat=self.main_content.map.center[0], lon=self.main_content.map.center[1]),
                        zoom=self.main_content.map.zoom
                    )
                )

            return self.main_content.map.fig
        
        @self.app.callback(
            Output('map', 'figure', allow_duplicate=True),
            Input('map', 'relayoutData'),
            prevent_initial_call=True
        )
        def map_interaction_callback(relayoutData: dict) -> go.Figure:
            r'''Callback triggered every time the user pans or zooms the map.'''
            
            if relayoutData is None or 'mapbox.center' not in relayoutData or 'mapbox.zoom' not in relayoutData: 
                return self.main_content.map.fig
            
            # Update the map's center and zoom level based on the user's interaction
            self.main_content.map.center = (relayoutData['mapbox.center']['lat'], relayoutData['mapbox.center']['lon'])
            self.main_content.map.zoom   = relayoutData['mapbox.zoom']
            
            # This callback is triggered on any pan/zoom event
            self.main_content.map.fig.update_layout(
                mapbox=dict(
                    center=dict(lat=self.main_content.map.center[0], lon=self.main_content.map.center[1]),
                    zoom=self.main_content.map.zoom
                )
            )

            return self.main_content.map.fig
        
        @self.app.callback(
            Output('map', 'figure', allow_duplicate=True),
            Output('sidebar-collapsible-content', 'children'),
            Input('language-dropdown', 'value'),
            prevent_initial_call=True
        )
        def language_selection_callback(value: str | None) -> tuple[go.Figure, Any] | tuple[dash.NoUpdate, dash.NoUpdate]:

            if value is None: return dash.no_update, dash.no_update

            # Value in the dropdown must be a string so we parse it to the right type
            lang = map_string_code_to_language(value)

            self.sidebar.update_layout_language(lang)
            self.main_content.elevation_plot.update_layout_language(lang)

            return self.main_content.map.fig, self.sidebar.main.children
                
class Map:
    r'''
    Class responsible for building the map figure and adding hikes to it.
    
    :param lat: Latitude for the map center.
    :param lon: Longitude for the map center.
    :param zoom: Initial zoom level for the map.
    '''

    def __init__(self, center_lat: float = 45.7640, center_lon: float = 4.8357, zoom: int = 10) -> None:

        self.build_map_figure(center_lat, center_lon, zoom=zoom)
        self._build_layout()

        self.center = (center_lat, center_lon)
        self.zoom   = zoom

        return 
    
    def build_map_figure(self, lat: float = 45.7640, lon: float = 4.8357, zoom: int = 10) -> None:
        r'''
        Initialize the map figure centered on the specified latitude and longitude.
        
        :param lat: Latitude for the map center.
        :param lon: Longitude for the map center.
        :param zoom: Initial zoom level for the map.
        '''

        self.fig = go.Figure()

        self.fig.update_layout(
            template='plotly_white',
            mapbox=dict(
                style='open-street-map',
                center=dict(lat=lat, lon=lon),
                zoom=zoom
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(color='#2c3e50', family='Open Sans, sans-serif'),
            margin=dict(l=0, r=0, t=0, b=0),
        )
        
        self.highlighted_point = go.Scattermapbox(
            mode="markers",
            lon=[4.773566],
            lat=[45.736296],
            showlegend=False,
            marker=dict(size=12, color='black', symbol='circle'),
            hoverinfo='none',
            name='point'
        )

        self.fig.add_trace(self.highlighted_point)

        return
    
    def _build_layout(self) -> None:
        r"""Build the map container with the initialized figure."""

        self.layout = html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(
                            id='map',
                            figure=self.fig,
                            config={'displayModeBar': False, 'scrollZoom': True},
                            style={'height': '100%', 'width': '100%'}
                        )
                    ],
                    className='p-4',
                    style={'height': '100%', 'width': '100%'}
                )
            ],
            className='flex-fill', 
            style={'height': '60%', 'width': '100%'}
        )

        return
    
    def add_hikes_to_map(self, hikes_data: dict) -> None:
        r'''Add all hikes from the loaded data to the map figure.'''

        for hike_data in hikes_data.values():
            self.add_hike_to_map(hike_data)
            
        return
    
    def add_hike_to_map(self, hike_data: dict) -> None:
        r'''Add a single hike to the map figure.'''

        lats  = [coord[0] for coord in hike_data['coords']]
        lons  = [coord[1] for coord in hike_data['coords']]
        color = hike_data['color']

        # Use Scattermapbox for Plotly mapbox-based figures
        self.fig.add_trace(go.Scattermapbox(
            mode="lines",
            lon=lons,
            lat=lats,
            showlegend=False,
            line=dict(width=4, color=color),
            opacity=1,
            hoverinfo='none',
        ))

        return

class ElevationPlot:
    r'''
    Class responsible for building the elevation profile plot.
    
    :param translations: A dictionary containing translations for different languages.
    :param default_language: default language used when the application starts
    :param color: color used to the line and the filled area
    '''

    def __init__(
            self, 
            translations     : dict, 
            default_language : LanguageEnum = LanguageEnum.ENGLISH,
            color            : str = 'black'
        ) -> None:

        # Component handling the language translation for this widget
        self.language_handler = LanguageHandler(translations, default_language)

        self.build_figure(color)
        self._build_layout()

        return
    
    def build_figure(self, color : str) -> None:
        r'''
        Build the elevation profile figure using Plotly.
        
        :param color: color of the line and filled area on the plot
        '''

        self.fig = go.Figure()

        self.trace = go.Scatter(
            x=[],  # Distance (km)
            y=[],  # Elevation (m)
            customdata=[],
            mode='lines',
            line=dict(color=color, width=2),
            fill='tozeroy',
            hovertemplate=self.hovertemplate,
            name='Elevation Profile'
        )

        self.fig.add_trace(self.trace)

        self.fig.update_layout(
            template='plotly_white',
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(color='#2c3e50', family='Open Sans, sans-serif'),
            margin=dict(l=0, r=0, t=0, b=0),
            hovermode='x unified',
            xaxis=dict(
                title=self.language_handler['xlabel'],
                unifiedhovertitle=dict(text=' ')
            ),
            yaxis=dict( title=self.language_handler['ylabel'])
        )

        return
    
    @property
    def hovertemplate(self) -> str:
        r'''Template used when hovering over the graph.'''

        return (
            f'<b>{self.language_handler["hovertemplate"]["distance"]}</b>:' + '%{x:.2f} km<br>'
            f'<b>{self.language_handler["hovertemplate"]["remaining_distance"]}</b>:' + '%{customdata[0]:.2f} km<br>'
            f'<b>{self.language_handler["hovertemplate"]["elevation"]}</b>:' + '%{y:.0f} m<br>'
            '<extra></extra>'
        )
    
    def _build_layout(self) -> None:
        r'''Build the layout for the elevation profile plot.'''

        self.layout = html.Div(
            [
                dcc.Graph(
                    id='elevation-plot',
                    figure=self.fig,
                    config={'displayModeBar': False},
                    style={'height': '80%', 'width': '100%'}
                )
            ],
            className='flex-fill',
            style={'flex' : '1 1 0', 'height': '20%', 'padding': '1rem', 'minHeight': 0, 'overflow': 'auto'}
        )

        return
    
    def update_layout_language(self, lang: LanguageEnum) -> None:
        r'''
        Update the language of the elements in the layout.

        :param: new language to apply
        '''

        self.language_handler.language = lang
        self.fig.update_layout(
            xaxis=dict(title=self.language_handler['xlabel']),
            yaxis=dict(title=self.language_handler['ylabel']),
        )

        self.fig.data[0].hovertemplate = self.hovertemplate

        return
    
    def add_elevation_data_to_plot(
            self, 
            distances  : list[float], 
            elevations : list[float]
        ) -> None:
        r'''
        Add elevation data to the plot figure.
        
        :param distances: cumulative distances since the beginning of the hike in km
        :param elevations: elevation in m at each point along the hike
        '''

        total_distance = distances[-1] if distances else 0.0
        remaining      = [[max(0.0, total_distance - d)] for d in distances]

        self.fig.data[0].x = distances
        self.fig.data[0].y = elevations
        self.fig.data[0].customdata = remaining

        return
    
class MainContent:
    r'''Class responsible for building the main content area of the application.'''

    def __init__(self, map: Map, elevation_plot: ElevationPlot) -> None:

        self.map            = map
        self.elevation_plot = elevation_plot

        self._build_layout()

        return
    
    def _build_layout(self) -> None:
        r'''Build the main content area containing the map and elevation plot.'''

        self.layout = html.Div(
            [
                self.map.layout,
                self.elevation_plot.layout
            ],
            className='flex-fill d-flex flex-column',
            style={'flex' : '1 1 0', 'height': '100vh', 'minHeight': 0, 'padding': '1rem', 'overflow': 'hidden', 'box-sizing': 'border-box'}
        )

        return
    