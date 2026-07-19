import dash
import typing
import dash_mantine_components   as     dmc
import dash_leaflet              as     dl
import plotly.graph_objects      as     go
import plotly.express            as     px
import numpy                     as     np
import pandas                    as     pd
from   numpy.typing              import NDArray
from   textwrap                  import dedent
from   dash_iconify              import DashIconify

from ..lang                      import LanguageHandler, LANGUAGE

def elevation_plot_layout(language_dict: dict) -> dmc.Stack:

    fig    = dash.dcc.Graph(
        id               = 'elevation-plot',
        responsive       = True,
        clear_on_unhover = True,
        config           = {
            'displayModeBar' : False,
            'scrollZoom'     : False,
            'doubleClick'    : False
        }
    )

    slider = dmc.Slider(
        w             = '100%', 
        h             = '10%', 
        hiddenFrom    = 'lg', 
        id            = 'elevation-plot-slider',
        updatemode    = "drag",
        thumbSize     = 30,
        thumbChildren = DashIconify(icon='gis:hiker'),
        label         = None,
        min           = 0

    )

    return dmc.Stack([fig, slider], h='30%', id='elevation-plot-stack', style={'display' : 'none'})

def map_page_layout(
        language_handler : LanguageHandler, 
        language         : LANGUAGE
    ) -> dmc.AppShellMain:
    r'''
    Widget containing the main content area of the application which contains the map and the elevation plot.
    
    :param language_handler: object the translation of the UI
    :param language: language used at startup
    '''
       
    map            = dash.html.Div(
        generate_leaflet_map_figure(), 
        id    = 'map-div', 
        style = {'height' : '100%'}
    )

    elevation_plot = elevation_plot_layout(language_handler[language]['elevation_plot'])

    return dmc.AppShellMain(
            dmc.Stack([map, elevation_plot], id = 'map-page'),
        style = {'width' : '100%', 'height' : '100vh'},
        id    = 'appshell-main'
    )

def generate_leaflet_map_figure(
        lon  : float = 4.8357, 
        lat  : float = 45.7640,
        zoom : int   = 10
    ) -> dl.Map:
    r'''
    Generate an empty leaflet figure serving as baseline every time the map has to be updated.

    :param lon: center's longitude
    :param lat: center's latitude
    :param zoom: zoom level
    '''

    layer_control = generate_layer_control()

    return dl.Map(
        children = [
            layer_control,
            dl.FullScreenControl(),
            dl.ScaleControl(position="bottomright"),
            dl.MeasureControl(
                position          = "topleft",
                primaryLengthUnit = "kilometers",
                primaryAreaUnit   = "hectares",
                activeColor       = "#214097",
                completedColor    = "#972158",
            ),
        ],
        center   = [lat, lon],  # type: ignore
        zoom     = zoom,
        id       = 'map', 
        style    = {'zIndex': 0},
    ) # type: ignore

def generate_base_layers() -> list[dl.BaseLayer | dl.LayerGroup | dl.CircleMarker]:
    r'''Generate the base layers used as map background.'''

    return [
        dl.BaseLayer(
            dl.TileLayer(url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", attribution='© OpenStreetMap contributors'),
            name    = "OSM", # type: ignore
            checked = True,
            id      = 'map-layer-OSM'
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
        dl.BaseLayer(
            dl.TileLayer(url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attribution='© Stadia Maps © Stamen Design © OpenMapTiles © OpenStreetMap contributors '),
            name    = "Satellite", # type: ignore
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

def generate_new_figure(
        distances  : NDArray[np.floating], 
        elevations : NDArray[np.floating], 
        color      : str
    ) -> go.Figure:
    r'''
    Generate a new figure for the elevation plot.

    :param distances: distances in km shown on the x-axis
    :param elevations: elevations in m shown on the y-axis
    :param color: color of the path

    :returns: the new figure
    '''
    
    fig = go.Figure()

    # We convert elevations to km to match distances
    delta_elevations = np.append([np.nan], elevations[1:] - elevations[:-1]) / 1000
    delta_distances  = np.append([np.nan], distances[1:]  - distances[:-1])
    slope            = np.abs(delta_elevations) / delta_distances * 100

    data = pd.DataFrame({
        'distances'           : distances, 
        'elevations'          : elevations, 
        'remaining_distances' : -(distances - distances[-1]),
        'slope'               : slope
    })

    fig = px.line(
        data_frame    = data,
        x             = distances,
        y             = elevations,
        custom_data   = ['remaining_distances', 'slope']
    )

    fig.update_layout(
        margin      = dict(l=0, r=0, t=0, b=0),
        xaxis_title = "Distance (km)",
        yaxis_title = "Elevation (m)",
        hovermode   = 'x',
        xaxis       = {'fixedrange' : True},   # Lock x-axis (no zoom/pan)
        yaxis       = {'fixedrange' : True},   # Lock x-axis (no zoom/pan)
        dragmode    = False,
        showlegend  = False,
    )

    fig.update_xaxes(
        showspikes     = True,
        spikemode      = "across",
        spikethickness = 1, 
        spikedash      = "dot", 
        spikecolor     = "#888",
    )

    fig.update_traces(
        line = {'color' : color, 'width' : 3},
        hovertemplate=dedent('''\
            <extra></extra>
            <b>Distance:</b> %{x:.1f} km<br>
            <b>Distance to end:</b> %{customdata[0]:.1f} km<br>
            <b>Elevation:</b> %{y:.0f} m<br>
            <b>Slope:</b> %{customdata[1]:.1f}%
        '''),
        name = ''
    )

    return fig