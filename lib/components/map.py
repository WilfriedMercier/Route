import dash
import plotly.graph_objects as     go
from   ..lang               import LanguageEnum, LanguageHandler

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

        self.layout = dash.html.Div(
            [
                dash.html.Div(
                    [
                        dash.dcc.Graph(
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
    :param color: color used for the line and the filled area
    '''

    def __init__(
            self, 
            translations     : dict, 
            default_language : LanguageEnum = LanguageEnum.ENGLISH,
            color            : str = 'black'
        ) -> None:

        # Component handling the language translation for this widget
        self.language_handler = LanguageHandler(translations, default_language)

        self._build_figure(color)
        self._build_layout()

        return
    
    def _build_figure(self, color: str) -> None:
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
            name='Elevation'
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
            yaxis=dict(title=self.language_handler['ylabel'])
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

        self.layout = dash.html.Div(
            [
                dash.dcc.Graph(
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
            elevations : list[float],
            color      : str
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

        

        self.fig.update_traces(
            line_color = color,
            selector   = {'name' : 'Elevation'}

        )

        return
    
class MapPage:
    r'''
    Class responsible for building the main content area of the application which contains the map and the elevation plot.
    
    :param lat: Latitude for the map center.
    :param lon: Longitude for the map center.
    :param zoom: Initial zoom level for the map.
    :param translations: A dictionary containing translations for different languages.
    :param default_language: default language used when the application starts
    :param color: default color used for the line and the filled area in the elevation plot
    '''

    def __init__(
            self, 
            lat              : float, 
            lon              : float, 
            zoom             : int,
            translations     : dict[str, dict],
            default_language : LanguageEnum,
            color            : str
        ) -> None:

        self._map            = Map(lat, lon, zoom)
        self._elevation_plot = ElevationPlot(
            {lang : translation['elevation_plot'] for lang, translation in translations.items()}, 
            default_language,
            color = color
        )

        self._build_layout()

        return
    
    @property
    def map(self) -> Map: return self._map

    @property
    def elevation_plot(self) -> ElevationPlot: return self._elevation_plot
    
    def _build_layout(self) -> None:
        r'''Build the main content area containing the map and elevation plot.'''

        self.layout = dash.html.Div(
            [self._map.layout, self._elevation_plot.layout],
            className='flex-fill d-flex flex-column',
            style={'flex' : '1 1 0', 'height': '100vh', 'minHeight': 0, 'padding': '1rem', 'overflow': 'hidden', 'box-sizing': 'border-box'}
        )

        return
    
    def update_layout_data(
            self, 
            distances  : list[float], 
            elevations : list[float],
            color      : str
        ) -> None:

        self.elevation_plot.add_elevation_data_to_plot(distances, elevations, color)

        return
    