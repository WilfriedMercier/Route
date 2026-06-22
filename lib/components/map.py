import dash
import plotly.graph_objects      as     go
import dash_mantine_components   as     dmc
import dash_bootstrap_components as     dbc
from   dash_iconify              import DashIconify

def map_style_button_layout(style: str) -> dmc.Button:
    r'''
    Custom button widget used in the widget allowing to switch map styles.

    :param style: default style
    '''

    figure = go.Figure()
    figure.update_layout(   
        template      = 'plotly_white',
        paper_bgcolor = 'white',
        plot_bgcolor  = 'white',
        font          = {'color' : '#2c3e50', 'family' : 'Open Sans, sans-serif'},
        margin        = {'l' : 0, 'r' : 0, 't' : 0, 'b' : 0},
        width         = 50,
        height        = 150,
        mapbox        = {
            'center' : {'lat' : 41.89860997999514, 'lon' : 12.477528109879714}, 
            'zoom'   : 14,
            'style'  : style
        }
    )

    figure.add_trace(
        go.Scattermapbox(
            lat       = [41.89860997999514], 
            lon       = [12.477528109879714],
            mode      ='markers',
            marker    = {'size' : 1, 'color' : 'rgba(0,0,0,0)'}, # Invisible dot to trigger render
            hoverinfo = 'none'
        )
    )

    graph = dash.dcc.Graph(
        figure = figure,
        config = {'staticPlot' : True}
    )

    return dmc.Button(
        graph, 
        className = 'map-style-button',
        id        = {'type' : 'map-style-button', 'index' : style}
    )
    
def map_style_selector_layout() -> dash.html.Div:
    r'''A widget that allows to select different map styles.'''

    buttons = []

    for pos, style in enumerate(('carto-positron', 'carto-darkmatter', 'open-street-map')):
        buttons.append(map_style_button_layout(style))

    return dash.html.Div(
        dmc.HoverCard([
                dmc.HoverCardTarget(DashIconify(icon='fluent-mdl2:map-layers', height=35, width=35)),
                dmc.HoverCardDropdown(buttons, style={'height' : '75px'}),
            ],
            position = 'left'
        ),
        className = 'div-map-style-selector'
    )

def map_layout(lat: float, lon: float, zoom: int, hikes_data: dict):
    r'''
    Widget containing the map figure.
    
    :param lat: Latitude for the map center
    :param lon: Longitude for the map center
    :param zoom: Initial zoom level for the map
    :param hikes_data: hike information to add to the figures
    '''

    highlighted_point = go.Scattermapbox(
        mode       = "markers",
        lon        = [4.773566],
        lat        = [45.736296],
        showlegend = False,
        marker     = {'size' : 12, 'color' : 'black', 'symbol' : 'circle'},
        hoverinfo  = 'none',
        name       = 'point',
    )

    fig = go.Figure(
        highlighted_point,
        layout = {
            'template'      : 'plotly_white',
            'mapbox'        : {
                    'style' : 'open-street-map', 
                    'center' : {'lat' : lat, 'lon' : lon}, 
                    'zoom' : zoom
            },
            'paper_bgcolor' : 'white',
            'plot_bgcolor'  : 'white',
            'font'          : {'color' : '#2c3e50', 'family' : 'Open Sans, sans-serif'},
            'margin'        : {'l' : 0, 'r' : 0, 't' : 0, 'b' : 0},
        }
    )

    add_hikes_to_map(fig, hikes_data)
    
    style_selector = map_style_selector_layout()

    return dash.html.Div([
            dash.dcc.Graph(
                id     = 'map',
                figure = fig,
                config = {'displayModeBar': False, 'scrollZoom': True}
            ),
            style_selector
        ],
        className = 'div-full-relative'
    )
    
def add_hikes_to_map(fig: go.Figure, hikes_data: dict[str, dict]) -> None:
    r'''
    Add all hikes from the loaded data to the map figure.
    
    :param fig: map figure
    :param hikes_data: dictionary containing as key the name of the hike and as values a dictionary with hike properties
    '''

    for name, data in hikes_data.items(): add_hike_to_map(fig, name, data)
        
    return
    
def add_hike_to_map(fig: go.Figure, hike_name: str, hike_data: dict) -> None:
    r'''
    Add a single hike to the map figure.
    
    :param fig: map figure
    :param hike_name: name of the hike
    :param hike_data: dictionary with hike properties
    '''

    lats  = [coord[0] for coord in hike_data['coords']]
    lons  = [coord[1] for coord in hike_data['coords']]
    color = hike_data['color']

    # Use Scattermapbox for Plotly mapbox-based figures
    fig.add_trace(go.Scattermapbox(
        mode       = "lines",
        lon        = lons,
        lat        = lats,
        showlegend = False,
        line       = {'width' : 4, 'color' : color},
        opacity    = 1,
        hoverinfo  = 'none',
        name       = hike_name
    ))

    return

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

def map_page_layout(lat: float, lon: float, zoom: int, hikes_data: dict) -> dbc.Stack:
    r'''
    Widget containing the main content area of the application which contains the map and the elevation plot.
    
    :param lat: Latitude for the map center
    :param lon: Longitude for the map center
    :param zoom: Initial zoom level for the map
    :param hikes_data: hike information to add to the figures
    '''

    map = map_layout(lat, lon, zoom, hikes_data)
       
    return dbc.Stack(map, id = 'map-page') #dash.html.Div(self._elevation_plot.layout) #, id='elevation-plot-flex-div')