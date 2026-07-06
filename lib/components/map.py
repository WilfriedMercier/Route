import dash
import dash_bootstrap_components as     dbc
import dash_leaflet              as     dl

"""
class ElevationPlot(BaseWidget):
    r'''
    Class responsible for building the elevation profile plot.
    
    :param app: The Dash application instance
    :param color: color used for the line and the filled area
    '''

    def __init__(self, app: dash.Dash, color: str = 'black') -> None:

        super().__init__(app)

        self._hovertemplate = (
            f'<b>{self.app.lang['elevation_plot']["hovertemplate"]["distance"]}</b>:' + '%{x:.2f} km<br>'
            f'<b>{self.app.lang['elevation_plot']["hovertemplate"]["remaining_distance"]}</b>:' + '%{customdata[0]:.2f} km<br>'
            f'<b>{self.app.lang['elevation_plot']["hovertemplate"]["elevation"]}</b>:' + '%{y:.0f} m<br>'
            '<extra></extra>'
        )

        self._init_figure(color)
        self._init_layout()

        return

    @property
    def hovertemplate(self) -> str: return self._hovertemplate
    
    def _init_figure(self, color: str) -> None:
        r'''
        Initialize the elevation profile figure using Plotly.
        
        :param color: color of the line and filled area on the plot
        '''

        self.fig = go.Figure()

        self.trace = go.Scatter(
            x             = [],  # Distance (km)
            y             = [],  # Elevation (m)
            customdata    = [],
            mode          = 'lines',
            line          = {'color' : color, 'width' : 2},
            fill          = 'tozeroy',
            hovertemplate = self.hovertemplate,
            name          = 'Elevation'
        )

        self.fig.add_trace(self.trace)

        self.fig.update_layout(
            template      = 'plotly_white',
            paper_bgcolor = 'white',
            plot_bgcolor  = 'white',
            font          = {'color' : '#2c3e50', 'family' : 'Open Sans, sans-serif'},
            margin        = {'l' : 0, 'r' : 0, 't' : 0, 'b' : 0},
            hovermode     = 'x unified',
            xaxis         = {
                'title'             : self.app.lang['elevation_plot']['xlabel'],
                'unifiedhovertitle' : {'text' : ' '}
            },
            yaxis         = {'title' : self.app.lang['elevation_plot']['ylabel']}
        )

        return
    
    def _init_layout(self) -> None:
        r'''Initialize the layout for the elevation profile plot.'''

        self._layout = dash.dcc.Graph(
            id     = 'elevation-plot',
            figure = self.fig,
            config = {'displayModeBar': False},
        )

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
        :param color: color of the line plot
        '''

        total_distance = distances[-1] if distances else 0.0
        remaining      = [[max(0.0, total_distance - d)] for d in distances]

        self.fig.data[0].x          = distances
        self.fig.data[0].y          = elevations
        self.fig.data[0].customdata = remaining

        self.fig.update_traces(
            line_color = color,
            selector   = {'name' : 'Elevation'}

        )

        return
"""

def map_page_layout() -> dbc.Stack:
    r'''Widget containing the main content area of the application which contains the map and the elevation plot.'''
       
    return dbc.Stack(
        generate_leaflet_map_figure(), 
        id = 'map-page'
    ) #dash.html.Div(self._elevation_plot.layout) #, id='elevation-plot-flex-div')

def generate_leaflet_map_figure(
        lon  : float | None = None, 
        lat  : float | None = None,
        zoom : int   | None = None
    ) -> dl.Map:
    r'''
    Generate an empty leaflet figure serving as baseline every time the map has to be updated.

    :param lon: center's longitude
    :param lat: center's latitude
    :param zoom: zoom level
    '''

    if lon is None  : lon  = 4.8357
    if lat is None  : lat  = 45.7640
    if zoom is None : zoom = 10

    layer_control = generate_layer_control()

    figure = dl.Map(children=[
            layer_control, 
            dl.FullScreenControl(),
            dl.ScaleControl(position="bottomright"),
            dl.LocateControl(locateOptions={"enableHighAccuracy": True}),
            dl.MeasureControl(
                position          = "topleft",
                primaryLengthUnit = "kilometers",
                primaryAreaUnit   = "hectares",
                activeColor       = "#214097",
                completedColor    = "#972158",
            ),
        ], 
        center = [lat, lon], 
        zoom   = zoom, 
        id     = 'map', 
        style  = {'zIndex': 0},
    ) # type: ignore
    
    return figure

def generate_base_layers() -> list[dl.BaseLayer | dl.LayerGroup]:
    r'''Generate the base layers used as map background.'''

    return [
        dl.BaseLayer(
            dl.TileLayer(url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", attribution='© OpenStreetMap contributors'),
            name    = "OSM", # type: ignore
            checked = True
        ),
        dl.BaseLayer(
            dl.TileLayer(url='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attribution='© OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)'),
            name    = "Open topo", # type: ignore
            checked = False
        ),
        dl.BaseLayer(
            dl.TileLayer(url='https://tiles.stadiamaps.com/tiles/stamen_toner/{z}/{x}/{y}.png', attribution='© Stadia Maps © Stamen Design © OpenMapTiles © OpenStreetMap contributors '),
            name    = "Stamen toner", # type: ignore
            checked = False
        ),
        dl.BaseLayer(
            dl.TileLayer(url='https://tiles.stadiamaps.com/tiles/stamen_watercolor/{z}/{x}/{y}.jpg', attribution='© Stadia Maps © Stamen Design © OpenStreetMap contributors '),
            name    = "Stamen watercolor", # type: ignore
            checked = False
        ),
        dl.BaseLayer(
            dl.TileLayer(url='https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}.png', attribution='© Stadia Maps © Stamen Design © OpenMapTiles © OpenStreetMap contributors '),
            name    = "Stamen terrain", # type: ignore
            checked = False
        ),
    ]

def generate_layer_control(poly_lines: list[dl.Polyline] = []) -> dl.LayersControl:
    r'''
    Generate the layer control that contains map styles and hike paths.

    :param poly_lines: hike paths to show on the map
    '''

    layers = generate_base_layers()
    layers.append(dl.LayerGroup(poly_lines, id='map-polylines'))

    return dl.LayersControl(
        layers,
        position = "topright",
        id       = 'map-layer-control'
    )