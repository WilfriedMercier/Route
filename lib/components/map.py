import dash
import plotly.graph_objects      as     go
import dash_mantine_components   as     dmc
import dash_bootstrap_components as     dbc
from   dash_iconify              import DashIconify

from   .base                     import BaseWidget

class MapStyleButton(BaseWidget):

    def __init__(self, app: dash.Dash, style: str, idd: int) -> None:
        
        super().__init__(app)

        self._style = style
        self._id    = idd

        self._init_layout()
        self._register_callbacks()

        return
    
    @property
    def id(self) -> int: return self._id

    @property
    def style(self) -> str: return self._style
    
    def _init_layout(self) -> None:

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
                'style'  : self.style
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

        graph =  dash.dcc.Graph(
            id     = f'map-style-map-{self.id}',
            figure = figure,
            config = {'staticPlot' : True}
        )

        self._layout = dmc.Button(
            graph, 
            className = 'map-style-button',
            id        = f'map-style-button-{self.id}'
        )

        return
    
    def _register_callbacks(self) -> None:

        def callback_map_style_change(_, figure_dict: go.Figure) -> go.Figure:

            print(self.style)
            figure = go.Figure(figure_dict)
            figure.update_layout(
                mapbox = {'style' : self.style}
            )

            return figure

        @self.app.callback(
            dash.Output('map', 'figure', allow_duplicate = True),
            dash.Input(f'map-style-button-{self.id}', 'n_clicks'),
            dash.State('map', 'figure'),
            prevent_initial_call = True
        )
        def callback_map_style_change_from_button(_, figure_dict: go.Figure) -> go.Figure:
            return callback_map_style_change(_, figure_dict)
        
        @self.app.callback(
            dash.Output('map', 'figure', allow_duplicate = True),
            dash.Input(f'map-style-map-{self.id}', 'clickData'),
            dash.State('map', 'figure'),
            prevent_initial_call = True
        )
        def callback_map_style_change_from_map(_, figure_dict: go.Figure) -> go.Figure:
            return callback_map_style_change(_, figure_dict)

        return
    
class MapStyleSelector(BaseWidget):
    r'''
    A widget that allows to select different map styles.
    
    :param app: The Dash application instance
    '''

    def __init__(self, app: dash.Dash) -> None:

        super().__init__(app)

        self._init_layout()

        return
    
    def _init_layout(self) -> None:

        self.buttons = []
        for pos, style in enumerate(('carto-positron', 'carto-darkmatter', 'open-street-map')):
            self.buttons.append(MapStyleButton(self.app, style, pos))

        self._layout = dash.html.Div(
            dmc.HoverCard([
                    dmc.HoverCardTarget(DashIconify(icon='fluent-mdl2:map-layers', height=35, width=35)),
                    dmc.HoverCardDropdown(
                        [button.layout for button in self.buttons],
                        style={'height' : '75px'}
                    ),
                ],
                position = 'left'
            ),
            className = 'div-map-style-selector'
        )

        return

class Map(BaseWidget):
    r'''
    Class responsible for building the map figure and adding hikes to it.
    
    :param app: The Dash application instance
    :param lat: Latitude for the map center.
    :param lon: Longitude for the map center.
    :param zoom: Initial zoom level for the map.
    '''

    def __init__(self, app: dash.Dash, lat: float, lon: float, zoom: int) -> None:

        super().__init__(app)

        self._init_map_figure()
        self._init_layout()

        self.set_zoom_and_center(lat, lon, zoom)

        return
    
    def _init_map_figure(self) -> None:
        r'''Initialize the map figure centered on the specified latitude and longitude.'''

        self.fig = go.Figure()

        self.fig.update_layout(
            template      = 'plotly_white',
            mapbox        = {'style' : 'open-street-map'},
            paper_bgcolor = 'white',
            plot_bgcolor  = 'white',
            font          = {'color' : '#2c3e50', 'family' : 'Open Sans, sans-serif'},
            margin        = {'l' : 0, 'r' : 0, 't' : 0, 'b' : 0},
        )
        
        self.highlighted_point = go.Scattermapbox(
            mode       = "markers",
            lon        = [4.773566],
            lat        = [45.736296],
            showlegend = False,
            marker     = {'size' : 12, 'color' : 'black', 'symbol' : 'circle'},
            hoverinfo  = 'none',
            name       = 'point'
        )

        self.fig.add_trace(self.highlighted_point)

        return
    
    def _init_layout(self) -> None:
        r"""Initialize the map container with the figure."""

        style_selector = MapStyleSelector(self.app)

        self._layout = dash.html.Div([
                dash.dcc.Graph(
                    id     = 'map',
                    figure = self.fig,
                    config = {'displayModeBar': False, 'scrollZoom': True}
                ),
                style_selector.layout
            ],
            className = 'div-full-relative'
        )

        return
    
    def set_zoom_and_center(self, lat: float, lon: float, zoom: int) -> None:
        r'''
        Update the zoom and center values of the map.
        
        .. note:
            To see the effect, the figure must be returned in a callback.

        :param lat: Latitude for the map center.
        :param lon: Longitude for the map center.
        :param zoom: Zoom level for the map.
        '''

        self.zoom   = zoom
        self.center = (lat, lon)

        self.fig.update_layout(
            mapbox = {'center' : {'lat' : lat, 'lon' : lon}, 'zoom' : self.zoom}
        )

        return
    
    def add_hikes_to_map(self, hikes_data: dict[str, dict]) -> None:
        r'''
        Add all hikes from the loaded data to the map figure.
        
        :param hikes_data: dictionary containing as key the name of the hike and as values a dictionary with hike properties
        '''

        for name, data in hikes_data.items():
            self.add_hike_to_map(name, data)
            
        return
    
    def add_hike_to_map(self, hike_name: str, hike_data: dict) -> None:
        r'''
        Add a single hike to the map figure.
        
        :param hike_name: name of the hike
        :param hike_data: dictionary with hike properties
        '''

        lats  = [coord[0] for coord in hike_data['coords']]
        lons  = [coord[1] for coord in hike_data['coords']]
        color = hike_data['color']

        # Use Scattermapbox for Plotly mapbox-based figures
        self.fig.add_trace(go.Scattermapbox(
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
    
    def hide_hike_from_map(self, index: int) -> None:
        r'''
        Hide the hike with the given index from the map.

        .. note:: 
            
            The first trace is the highlight marker, so the index is increased by 1

        :param index: index of the hike in the hike list
        '''

        self.fig.data[index + 1].visible = False
        return

    def show_hike_from_map(self, index: int) -> None:
        r'''
        Show the hike with the given index from the map.

        .. note:: 
            
            The first trace is the highlight marker, so the index is increased by 1

        :param index: index of the hike in the hike list
        '''

        self.fig.data[index + 1].visible = True
        return

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
    
class MapPage(BaseWidget):
    r'''
    Class responsible for building the main content area of the application which contains the map and the elevation plot.
    
    :param app: The Dash application instance
    :param lat: Latitude for the map center
    :param lon: Longitude for the map center
    :param zoom: Initial zoom level for the map
    :param color: default color used for the line and the filled area in the elevation plot
    '''

    def __init__(
            self,
            app   : dash.Dash,
            lat   : float, 
            lon   : float, 
            zoom  : int,
            color : str
        ) -> None:
    
        super().__init__(app)

        self._map            = Map(app, lat, lon, zoom)
        self._elevation_plot = ElevationPlot(app, color = color)

        self._init_layout()

        return
    
    @property
    def map(self) -> Map: return self._map

    @property
    def elevation_plot(self) -> ElevationPlot: return self._elevation_plot
    
    def _init_layout(self) -> None:
        r'''Initialize the main content area containing the map and elevation plot.'''

        self._layout = dbc.Stack(
            [
                self._map.layout
                #dash.html.Div(self._elevation_plot.layout) #, id='elevation-plot-flex-div')
            ],
            id = 'map-page'
        )

        return
    
    def update_layout_data(
            self,
            distances  : list[float], 
            elevations : list[float],
            color      : str,
            lat        : float,
            lon        : float,
            zoom       : int
        ) -> None:

        self.elevation_plot.add_elevation_data_to_plot(distances, elevations, color)
        self.map.fig.update_layout(
            mapbox= {
                'center' : {'lat' : lat, 'lon' : lon},
                'zoom'   : zoom
            }
        )

        return
    